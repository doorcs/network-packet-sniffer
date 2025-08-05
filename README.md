## scapy 라이브러리를 활용해 네트워크 트래픽을 분석해보자

### 아키텍처
<img width="658" height="430" alt="diagram" src="https://github.com/user-attachments/assets/f0cdfb22-81bc-4eba-87aa-4f2407d9e582" />

### 환경 설정
- 중앙 우분투 서버에 Docker 설치
```shell
sudo apt update
sudo apt install curl git # curl, git 설치

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh # 도커 설치 (docker compose도 함께 설치됨)
```

- 컨테이너 실행
```shell
git clone ...

cd docker
docker compose up -d
```


- 모니터링 대상 서버에서 agent.py 실행

  - Linux
  ```shell
  sudo apt update
  sudo apt install curl git # curl, git 설치

  curl -LsSf https://astral.sh/uv/install.sh | sh # uv 설치

  git clone ...
  uv sync

  sudo uv run ./src/agent.py # 권한 없이 그냥 실행하면 오류 발생!!
  ```
### 대시보드 확인
- http://`중앙 서버 IP`:`3000` 접속

  - id, password 입력  
-> 도커 디렉토리 안 `.env` 파일의 `GF_SECURITY_ADMIN_USER`, `GF_SECURITY_ADMIN_PASSWORD` 값. 기본값은 ID/PW 모두 `admin`

  - Dashboard -> New -> Import -> `Import via dashboard JSON model`  
**uid 값 변경 필요!!**

<img width="1582" height="1031" alt="대시보드" src="https://github.com/user-attachments/assets/26b503a9-84f3-4b8b-b713-98da57e112a1" />

> 데이터베이스 I/O 노이즈를 줄일 방법 생각해보기
