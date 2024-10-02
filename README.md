# 동아리 팀 빌딩 서비스

부경대학교 WAP 동아리에서 사용해주길 바라고 제작한 팀 빌딩 서비스의 서버 코드입니다.

---
### 프로젝트 소개

프로그래밍 동아리에서 한 학기 동안 진행할 프로젝트를 위해 팀을 빌딩하는 것은 중요한 일입니다. <br>
WAP 동아리에서는 정형화된 방식이 없고 그때그때마다 방법이 달라 정보를 얻기가 쉽지 않습니다. <br>
이를 도와주기 위한 팀 빌딩 및 회원 관리 서비스를 개발하게 되었습니다.

### 배포 링크

서버 -> [SWAGGER](https://api.whatmeow.shop/swagger) <br>
프론트 -> [관리자](https://admin.whatmeow.shop), [사용자](https://test.whatmeow.shop) <br>
자세한 내용은 [Notion](https://taewon-note.notion.site/W-A-P-ec03ad1ba4e64dbf8c127e5dfce7c564?pvs=4)에서 볼 수 있습니다.

---
### 기술스택
<div align=left> 
  <img src="https://img.shields.io/badge/django-009688?style=for-the-badge&logo=django&logoColor=white" width=100 height=50/>
  <img src="https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white" width=100 height=50/>
  <img src="https://img.shields.io/badge/celery-37814A?style=for-the-badge&logo=celery&logoColor=white" width=100 height=50/>
  <img src="https://img.shields.io/badge/awsEC2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white" width=100 height=50/>
  <img src="https://img.shields.io/badge/redis-FF4438?style=for-the-badge&logo=redis&logoColor=white" width=100 height=50/>
  <img src="https://img.shields.io/badge/nginx-009639?style=for-the-badge&logo=nginx&logoColor=white" width=100 height=50/>
</div>

---
### 제공 기능

- 깃허브 소셜 로그인
- 임원진(관리자)의 팀/회원 관리 ex) 회원가입 후 승인 여부
- 동아리원(일반회원)/임원진의 팀 빌딩 및 가입신청
- 내 활동내역 및 자기소개
- 팀장의 팀원 관리

---
### 기술적 의사결정

#### Redis 캐시 서버 도입

부하테스트 도구인 Locust를 활용해 부하가 크게 몰릴 것으로 예정되는 팀 빌딩 시간을 상정해 <br>
80개의 클라이언트가 1.5-2초 간격으로 유저 프로필, 팀 상세 페이지에 접근하는 상황으로 테스트를 진행했습니다.
![캐시적용전](https://github.com/user-attachments/assets/a58adbe6-f752-47cf-ae1a-ddcfb02762ba)

서버의 부족한 성능을 감안하더라도 평균 응답 시간이 3000ms로 사용자의 사용 경험에 큰 불편함이 있을 것으로 예상되었습니다.

![캐시적용후](https://github.com/user-attachments/assets/0212aff1-6fed-4ae6-82f8-85444db3bf94)

Redis를 활용해 캐시 적용 후 같은 조건으로 실시한 테스트입니다. <br>
캐시 서버에 데이터가 모여 캐시 히트율이 올라가면서 평균 응답 시간이 약 1000ms로 빨라져 약 66.7%의 향상률을 보였습니다.

#### Celery-Beat 조회수 업데이트 로직

- 중복 조회 방지 로직
   조회 시에 조회수를 ++1 하는 로직은 중복 유저의 조회인 경우에도 합산되는 사태가 벌어질 수 있습니다. <br>
   따라서 중복 여부를 판단하여 조회수 합산을 해야합니다. <br>
   이 방법으로 쿠키를 사용하는 방법은 쿠키를 삭제하는 방식, 쿠키의 메모리에 한계가 있는 점을 고려하여 <br>
   Redis와 Celery-Beat를 활용해 조회수를 집계해보기로 했습니다. 물론, 이 기술에 익숙해지기 위함의 이유도 존재합니다.

   하루에 한 번만 조회수가 집계되는 것을 기준으로 구현했습니다. <br>
   > 1. 게시물 조회 시 Redis에 view_{post_id} 키에 {ip}_{user_id} 밸류를 SADD 명령으로 추가 <br>
   > 2. Redis는 SADD 명령으로 데이터 추가 성공 시 1, 실패 시 0을 반환 <br>
   > 3. 반환받은 데이터를 통해 중복 조회인지 아닌지 판별 가능 <br> <br>

   Crontab으로 자정마다 Celery Beat 스케쥴링을 통해 조회수 관련 Redis 데이터를 삭제 해 조회수를 다시 집계할 수 있도록 했습니다.

  ![image](https://github.com/user-attachments/assets/7f7ba22f-5064-4f14-a7f5-18fa3170d1ae)

   
- 캐시된 게시물에 대한 조회수 업데이트 로직
   캐시 전략을 도입하게 되며 조회수 업데이트 로직도 변화를 주어야 했습니다. <br>
   DB I/O를 줄이기 위해 캐시를 사용하는데 조회수가 증가할 때마다 DB에 업데이트 할 수는 없었기 때문입니다. <br>
   <br>
   > 1. 게시물을 조회할 때 위 로직을 통해 캐시 데이터에 조회수를 ++1 <br>
   > 2. 여기에 추가적으로 조회수가 업데이트 된 게시물이라면 Redis의 view_updated 키에 {post_id}를 SADD 명령으로 추가 <br>
   > 3. 캐시 데이터의 지속시간을 5분으로 설정해놨으므로 3분마다 Celery Beat를 활용해 DB에 bulk update

   ![image](https://github.com/user-attachments/assets/6f4eb5d0-d2bf-4ad5-8ed0-77adc535a0ec)


---
