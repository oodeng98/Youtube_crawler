# Youtube_crawler

매일 유튜브 인기 동영상 리스트를 추출하고, 댓글들을 저장하는 코드를 짜는 것이 목표  
대댓글도 물론 포함이며, 각 주제별 인기 동영상이 있을텐데 저장할 수 있는 모든 데이터를 저장하는 것이 일단 목표

현재 해야하는 것   
1, videos().list 에서 part='snippet, statistics'로 실험해보기  
2, 데이터 중에서 겹치는 부분과 겹치지 않는 부분을 정리해서 데이터 스키마 구현  
3, 인기 동영상 댓글 저장 기능 