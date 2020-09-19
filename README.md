# 11-WeStock-backend README

# Introduction
* StockX - 패션, 수집품 리셀링 경매 중개 사이트(stockx.com)
* 개발기간 : 2020.08.31 ~ 2020.09.13(12일)
* 개발인원 : Front-end 4명(이영섭, 김동호, 류상욱, 송다슬), Back-end 3명(이충희, 이태현, 왕민욱)
* [Front-end Github](https://github.com/wecode-bootcamp-korea/11-WeStock-frontend)
* [Back-end Github](https://github.com/wecode-bootcamp-korea/11-WeStock-backend)

# Achivement
- 1차 프로젝트 이후 느낀 부족한 부분을 보완하면서 더 원활한 협업이 진행 될 수 있도록 노력
- Scrum 개발 방법에 더욱 익숙해지고, 프로젝트 진행에 도움이 되는 도구들에 더욱 숙달
- 많은 양의 데이터를 수집해보고, 이를 다루면서 서버의 가장 큰 역할인 DB를 효율적으로 제어
- 하나 이상의 소셜 로그인을 적용

# Demo Video


# Modeling
![Imgur](https://i.imgur.com/PvdiLsZ.png)

# Skill Stacks
* Python
* Django
* Bcrypt
* JWT
* MySQL
* Redis
* Goole, Kakao Social API
* Django ORM
* SQL RAW Query
* CORS headers
* Git, Github
* AWS EC2, RDS
* Docker

# Apps
* User
	- 유저정보 저장
  - 회원가입 / 로그인
  	- 가입 정보 유효성 검사
    - 패스워드 암호화
    - JWT Tocken을 통한 사용자 식별
    - 카카오, 구글 계정을 사용한 회원가입 및 로그인
  - 로그인 상태인지 확인하는 데코레이터 함수
 
* Sale
  - 제품 검색
  - 제품 경매 현황 
   
* Product
  - 전체 리스트
    - 전체 제품의 간략한 정보를 제공
    - 선택한 기준에 따라 제품 리스트를 정렬
  - 제품 상세
    - 개별 상품에 대한 상세 정보를 제공

  
# Settings
* AWS EC2 인스턴스 세팅
* AWS RDS MySQL 세팅
* Redis를 사용한 DB 쿼리 결과 캐싱
* unit test 진행
* github를 통한 프로젝트 버전 관리
* Docker를 사용한 프로젝트 배포

# API Documentation
