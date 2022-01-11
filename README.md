# hanghae_D8

항해 1주차 미니프로젝트 - 밸런스 게임 



## 1. 8조의 프로젝트 제목 및 간단설명

### <프로젝트명 : 골라보세요 밸런스게임!>

- 고깃집에서 후식은 당연히 물냉 vs. 비냉
- 나는 중국집 가면 짜장 vs. 짬뽕
- 복숭아는 당연히 딱딱한 복숭아 vs. 물렁한 복숭아

도대체 어떤것이 정답인지 알 수 없는 황금 밸런스 질문들 사이에서 나의 의견을 강력하게 표현 해 보세요!
댓글로 추가 의견을 써 주셔도 좋습니다. 상대를 설득할 수만 있다면요!

득표수가 비슷한 게임은 특별한 표시가 되어 더욱 더 많은 사람들의 의견을 모을 수 있습니다.

## 2. 웹페이지의 와이어프레임

<img src="https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FdmS21p%2FbtrqmJk0On6%2F3Dn8lLZBNB63spOYIxt8oK%2Fimg.png" width="1000px " height="800px">

## 3. 개발해야 하는 기능들 (API)

| 담당 | 기능 | Method | URL | request | response |
| --- | --- | --- | --- | --- | --- |
| 공정용 | 벨런스 게임 메인페이지 | GET | /api/home | {’img_url_left’:img_url_left, ‘img_url_right’:img_url_right, ‘suggestion_left’:suggestion_left, ‘suggestion_right’:suggestion_right, ‘likes’:likes, ‘views’:views, ‘date’:date} | 입력된 게시글 전부 받아오기, 투표수, 조회수 |
| 구름 | 게임 작성 | POST | /api/post | {’name’: name,’img_title_left’: img_title_left,’img_title_right’: img_title_right, ’img_url_left’: img_url_left, ’img_url_right’: img_url_right, ’contents’: contents,} | 게임명, 게임 대표 사진, 게시글 HTML 에디터, 등록 메세지 |
| 최세연 | 게임 투표 | PATCH,GET | /api/detail | {‘count_right’:count-right, ‘count-left’:count-left} | 검색 결과 리뷰 리스트 |
| 최세연 | 댓글 기능 구현 | POST | /api/detail | {’name’:name, ‘contents’:contents} | 댓글 추가, 수정, 삭제 |
| 구름 | 게임 수정 및 삭제 | DELETE,PATCH | /api/detail | {’_id’:_id, ’title’:title, ’contents':contents} | 게임 수정, 삭제 |
| 정요한 | 회원가입하기 | POST | /api/regist | {’user_id’:user_id,’user_pw’:user_pw, ’pass_check':pass_check, ’username’:username} | 공백 체크, 중복 체크 |
| 정요한 | 로그인하기 | POST | /api/login | {’user_id’:user_id,’user_pw’:user_pw} |  |
| 공정용 | 인기순 등 필터페이지 |  |  |  |  |
| 공정용, 최세연 | 조회수 |  |  |  |  |
| 공정용, 최세연 | 추천수 |  |  |  |  |

## 4. public github repo 주소

[https://github.com/John3210of/hanghae_D8](https://github.com/John3210of/hanghae_D8)
