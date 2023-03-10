# Youtube_crawler

### 목표
#### 1, 유튜브 API를 활용하여 매 시간 각 카테고리 별 인기 동영상 목록 저장 - 완료
#### 2, 유튜브 API를 활용하여 인기 동영상 목록에 올라온 채널의 구독자 추이 저장하기 - 진행중
#### 3, 인기 동영상에 달린 모든 댓글 저장 후 특정 사용자가 작성한 댓글 검색 기능 지원
#### 4, 앞서 구현한 기능들을 지원하는 사이트 구현

### 데이터 구조 및 변수 설명
#### Table name: Youtube
#### Partition Key: Item(str)
#### sort key: Id(str) 

* Common index
  * publishedAt: str, 등록된 시간
* Video(Partition Key Value)
  * title: str, 비디오 제목
  * description: str, 비디오 설명
  * tags: list, 비디오에 달린 해시태그들
  * channelId: str, 비디오를 업로드한 채널의 ID
  * thumbnailFilePath: str, 썸네일 이미지 파일을 저장한 위치
  * thumbnailUrl: str, 썸네일 이미지 파일의 url
  * topicCategories: list, 비디오의 카테고리들
  * viewCount: int, 비디오의 조회수
  * likeCount: int, 비디오의 좋아요 수
  * commentCount: int, 비디오의 댓글 수
  * confirmationAt: str, 인기 동영상 순위를 확인한 시간 
  * rank: int, 비디오의 인기 급상승 순위
  * category: str, 비디오가 속한 인기 급상승의 카테고리
* Channel(Partition Key Value)
  * title: str, 채널 이름
  * description: str, 채널 설명
  * customUrl: str, 채널에서 @~ 부분
  * country: str, 채널의 국가
  * thumbnailFilePath: str, 썸네일 이미지 파일을 저장한 위치
  * viewCount: int, 채널의 총 조회수
  * subscriberCount: int, 채널의 구독자 수
  * videoCount: int, 채널의 총 비디오 수
  * topicCategories: str, 채널이 다루는 동영상의 카테고리들
  * confirmationAt
* Comment(Partition Key Value)
  * authorChannelId: str, 댓글 작성자 채널의 Id 
  * author: 댓글 작성자의 이름
  * textOriginal: 댓글 내용
  * likeCount: 댓글의 좋아요 수
  * videoId: 댓글이 작성된 비디오의 Id
  * originalComment: 이 댓글이 댓글인지 대댓글인지 판단, None이면 댓글, 대댓글이라면 원래 댓글의 commentId

#### 새롭게 배운 지식

##### Youtube API
* 앞으로 API KEY와 같은 중요한 키는 text가 아니라 ini파일에 저장하자
* requests로 API와 소통하는 방법도 있지만 이번 경우에는 googleapiclient.discovery.build를 활용하는 방법도 존재한다.
* Google Cloud에서 API 사용 인증을 받아야 한다. 자격증명이 존재하지 않으면 아예 사용이 불가능하다.
* API사용법은 구글에 검색하는 방법도 있지만 공식 문서를 먼저 활용하는 습관을 들이는 것이 추후 도움이 될 것 같다.
* 하루 10000개의 쿼리 할당량이 있지만 유튜브 측에 요청해서 올릴 수 있다. 하지만 그 전에 쿼리 사용량을 최적화하는 과정을 선행하자.
* 모든 데이터는 json 형태로 반환되며, API 공식 문서 사이트에서 직접 실행해 볼 수 있는 기능도 일부 지원한다.
* 날짜 데이터를 표기하는 표준 방식이 존재한다, https://ohgyun.com/416 이 글을 참고하면 좋음
* 유튜브 API로 가져오는 대부분의 시간 데이터는 UTC 시간대를 기준으로 한다.

##### AWS EC2(Ubuntu)
* 월별 750시간까지 무료
* 윈도우에서 ssh -i [key 파일 위치] ubuntu@[퍼블릭 IPv4 DNS]를 넣으면 프로그램 설치 없이 쉽게 EC2에 접속이 가능하다. 개인적으로 putty보다 이 방법을 권장한다.
* 이때 퍼블릭 IPv4 DNS를 고정하려면 탄력적 IP(Elastic IP)를 설정하면 된다.
* 인스턴스에 연결되어 있지 않은 탄력적 IP는 돈이 나가므로 조심하자. 물론 굉장히 소액이긴 하다.
* 리눅스와 우분투는 비슷하지만 다르다. 제발 만들때 리눅스인지 우분투인지 꼭 확인하자.
* 새로운 환경을 접하면 파이썬 버전을 꼭 확인해보자.(python --version or python3 --version)
* 문서가 있는 폴더를 삭제하는 명령어는 rm -rf이다.
* 실행중인 프로세스를 찾는 명령어는 ps aux, 이에 더해 파이썬 프로세스 목록을 확인하고 싶다면 ps aux | grep python을 시행하자.
* kill -9 [PID] 는 PID를 가진 프로세스를 중지시킨다.
* 로컬 컴퓨터에서 만든 프로그램을 다른 환경에서 실행하고 싶다면 pip list --format=freeze > requirements.txt 로 파일을 만들어서 같이 넘겨주자.
* 그 후 pip install -r requirements.txt를 실행하자, 참고로 requirements.txt는 관행적으로 사용되는 파일 이름으로, 앞으로도 이 이름을 사용하자.
* EC2 프리티어의 한달 사용 가능 시간은 750시간으로, 서버를 하나만 돌린다면 한달 내내 돌려도 충분하다.(아마도?)
* 특정 디렉토리의 용량을 확인하는 명령어는 du -sh [folder 이름], 현재 폴더에 있는 폴더 및 파일의 용량을 출력하는 명령여는 du -sh *이다.

#####  AWS DynamoDB
* 프리티어로 25GB의 용량을 사용할 수 있다.
* 25개의 프로비저닝된 쓰기 용량 유닛, 25개의 프로비저닝된 읽기 용량 유닛, 그리고 월별 2억개의 요청을 처리할 수 있는 용량이 주어진다.
* AWS S3와 연동이 쉬운 것으로 보인다. 직접 사용해보진 않았지만 클릭 몇번으로 S3로 데이터 전송이 가능하다.
* 공식 문서를 제외한 자료는 웬만하면 없다. 문제가 발생한다면 직접 부딪혀보는 방식으로 해결하게 된다.
* 파이썬으로 DynamoDB에 접근하고 싶다면 IAM에서 사용자를 추가하여 키를 받아야 한다.
* 권한 정책은 AmazonDynamoDBFullAccess 등 여러개가 있는데 DynamoDB검색해서 자신에게 어울리는 정책 설정하고 단 한번 주어지는 키 값을 저장해서 활용하면 된다. 키는 다시는 주어지지 않는다.  
* AWS CLI를 설치하고 aws configure 입력, 그 후 해당하는 값들을 설정하면 비로소 boto3.resource를 사용할 수 있다. 
* 함수로 DynamoDB에 접근하기 전에 데이터 구조를 완벽히 짜고 접근하는 것이 좋은 것 같다.
* 필자는 이번 프로젝트에서 일주일 넘게 데이터 구조를 갈아치우는 경험을 했다.
* Partition Key를 설계할 때 고려해야하는 부분
* query가 scan보다 비용 및 효율이 좋다, 하지만 Key-Value Nosql인 DynamoDB의 특성상 query를 하기가 어렵다.
* 그래서 글로벌 보조 인덱스(GSI)를 활용하는 듯 싶다. 로컬 보조 인덱스(LSI)와 기능 면에서 어떤 차이가 있는지는 모르겠다.
* LSI는 테이블 생성 이후 생성할 수 없는 반면 GSI는 테이블 생성 이후에도 설정할 수 있다.
* GSI는 테이블 내에 간단한 다른 테이블을 만들어준다고 생각하면 편한 듯 싶다.
* 유튜브 비디오 ID로 DynamoDB PK를 설정, 조회수로 SK를 설정했다면 좋아요 수를 기준으로 정렬하기 위해서는 scan과정이 필요하다.
* 그렇다면 GSI로 비디오 ID를 설정하고, 새로운 SK로 좋아요 수를 지정한다면 query로 쉽게 정렬할 수 있다.
* ProvisionedThroughputExceededException가 간헐적으로 발생, 보통 하나의 partition key에 너무 자주 접근해서 생기는 오류라고 하는데, 이를 해결할 방법을 아직 못찾음

##### AWS S3
* 프리티어로 5GB의 스토리지를 사용할 수 있고 20000건의 GET 요청, 2000건의 PUT 요청이 무료다.
* S3 Standard 기준으로 50TB까지 GB당 0.025USD(32.5원)가 월마다 청구된다.
* PUT, COPY, POST, LIST 요청 1,000개당 0.0045USD(5.2원), GET, SELECT 및 기타 모든 요청 1,000개당 0.00035USD(0.455원)이 청구된다.
* DynamoDB와 마찬가지로 S3에 접근하고 싶다면 IAM에서 사용자를 추가하여 키를 받거나 기존에 사용하고 있는 사용자에 권한을 추가해야 한다.


#### 번외
* https://wikidocs.net/book/5445  이거도 재미있어보임