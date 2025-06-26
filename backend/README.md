# PMS Backend API

프로젝트 관리 시스템(Project Management System) 백엔드 API

## 📋 목차

- [프로젝트 개요](# 프로젝트-개요)
- [기술 스택](# 기술-스택)
- [주요 기능](# 주요-기능)
- [설치 및 실행](# 설치-및-실행)
- [API 문서](# api-문서)
- [프로젝트 구조](# 프로젝트-구조)
- [환경 설정](# 환경-설정)
- [데이터베이스](# 데이터베이스)
- [개발 가이드](# 개발-가이드)

## 🎯 프로젝트 개요

PMS Backend API는 FastAPI 기반의 현대적인 프로젝트 관리 시스템 백엔드입니다. 사용자 관리, 프로젝트 추적, 작업 관리, 캘린더 기능을 제공하는 RESTful API입니다.

### 주요 특징

- 🚀 **FastAPI** 기반 고성능 비동기 API
- 🔐 **JWT 인증** 및 역할 기반 접근 제어 (RBAC)
- 🗄️ **SQLAlchemy 2.0** ORM 및 비동기 데이터베이스 연결
- 📊 **Pydantic** 기반 데이터 검증
- 🔄 **Alembic** 데이터베이스 마이그레이션
- 📝 **자동 API 문서** (Swagger/OpenAPI)
- 🧪 **타입 힌팅** 및 IDE 지원

## 🛠 기술 스택

### 핵심 기술

- **Python 3.11+**
- **FastAPI** - 웹 프레임워크
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL** - 데이터베이스
- **Pydantic** - 데이터 검증
- **Alembic** - 데이터베이스 마이그레이션

### 인증 및 보안

- **JWT (JSON Web Tokens)** - 인증
- **bcrypt** - 비밀번호 해싱
- **OAuth2** - 외부 인증 지원

### 개발 도구

- **uvicorn** - ASGI 서버
- **pytest** - 테스트 프레임워크
- **black** - 코드 포매터
- **flake8** - 린터

## ✨ 주요 기능

### 👥 사용자 관리

- 회원가입/로그인/로그아웃
- 프로필 관리
- 역할 기반 접근 제어 (Admin, Project Manager, Developer, Viewer)
- 비밀번호 재설정
- 사용자 활동 로그

### 📁 프로젝트 관리

- 프로젝트 CRUD 작업
- 프로젝트 멤버 관리
- 프로젝트 상태 및 우선순위 설정
- 프로젝트 코멘트 및 첨부파일
- 프로젝트 통계 및 대시보드

### ✅ 작업 관리

- 작업 CRUD 작업
- 작업 할당 및 상태 관리
- 작업 코멘트 및 첨부파일
- 시간 추적 (Time Tracking)
- 작업 태그 및 분류
- 칸반 보드 및 간트 차트

### 📅 캘린더 관리

- 이벤트 생성 및 관리
- 반복 이벤트 지원
- 캘린더 공유
- 이벤트 참석자 관리
- 알림 설정

## 🚀 설치 및 실행

### 사전 요구사항

- Python 3.11 이상
- PostgreSQL 12 이상
- pip 또는 uv (권장)

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd pms-backend
```

### 2. 가상환경 설정

```bash
# Python venv 사용
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 또는 uv 사용 (권장)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. 의존성 설치

```bash
# pip 사용
pip install -r requirements.txt

# 또는 uv 사용 (권장)
uv pip install -r requirements.txt
```

### 4. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 편집하여 설정값 입력
```

### 5. 데이터베이스 설정

```bash
# PostgreSQL 데이터베이스 생성
createdb pms_db

# 마이그레이션 실행
alembic upgrade head
```

### 6. 서버 실행

```bash
# 개발 서버 실행
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 또는 스크립트 사용
python -m src.main
```

### 7. API 문서 확인

브라우저에서 다음 URL을 방문하세요:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **OpenAPI JSON**: <http://localhost:8000/api/v1/openapi.json>

## 📚 API 문서

### 인증

모든 보호된 엔드포인트는 Authorization 헤더에 Bearer 토큰이 필요합니다:

```bash
Authorization: Bearer <your-jwt-token>
```

### 주요 엔드포인트

#### 인증 관련

- `POST /api/v1/auth/register` - 회원가입
- `POST /api/v1/auth/login` - 로그인
- `POST /api/v1/auth/refresh` - 토큰 갱신
- `POST /api/v1/auth/logout` - 로그아웃

#### 사용자 관리

- `GET /api/v1/users/` - 사용자 목록 조회
- `GET /api/v1/users/{user_id}` - 사용자 정보 조회
- `PUT /api/v1/users/{user_id}` - 사용자 정보 수정
- `DELETE /api/v1/users/{user_id}` - 사용자 삭제

#### 프로젝트 관리

- `GET /api/v1/projects/` - 프로젝트 목록 조회
- `POST /api/v1/projects/` - 프로젝트 생성
- `GET /api/v1/projects/{project_id}` - 프로젝트 상세 조회
- `PUT /api/v1/projects/{project_id}` - 프로젝트 수정
- `DELETE /api/v1/projects/{project_id}` - 프로젝트 삭제

#### 작업 관리

- `GET /api/v1/tasks/` - 작업 목록 조회
- `POST /api/v1/tasks/` - 작업 생성
- `GET /api/v1/tasks/{task_id}` - 작업 상세 조회
- `PUT /api/v1/tasks/{task_id}` - 작업 수정
- `DELETE /api/v1/tasks/{task_id}` - 작업 삭제

#### 헬스 체크

- `GET /health` - 기본 헬스 체크
- `GET /health/detailed` - 상세 헬스 체크

## 📁 프로젝트 구조

``` bash
backend/
├── src/
│   ├── api/                 # API 라우터
│   │   ├── __init__.py
│   │   ├── auth.py         # 인증 관련 API
│   │   ├── users.py        # 사용자 관리 API
│   │   ├── projects.py     # 프로젝트 관리 API
│   │   ├── tasks.py        # 작업 관리 API
│   │   ├── calendar.py     # 캘린더 API
│   │   ├── health.py       # 헬스 체크 API
│   │   └── system.py       # 시스템 정보 API
│   ├── core/               # 핵심 설정
│   │   ├── __init__.py
│   │   ├── config.py       # 애플리케이션 설정
│   │   ├── database.py     # 데이터베이스 연결
│   │   ├── dependencies.py # 의존성 주입
│   │   └── db_utils.py     # 데이터베이스 유틸리티
│   ├── models/             # SQLAlchemy 모델
│   │   ├── __init__.py
│   │   ├── user.py         # 사용자 모델
│   │   ├── project.py      # 프로젝트 모델
│   │   ├── task.py         # 작업 모델
│   │   └── calendar.py     # 캘린더 모델
│   ├── schemas/            # Pydantic 스키마
│   │   ├── __init__.py
│   │   ├── auth.py         # 인증 스키마
│   │   ├── user.py         # 사용자 스키마
│   │   ├── project.py      # 프로젝트 스키마
│   │   ├── task.py         # 작업 스키마
│   │   ├── calendar.py     # 캘린더 스키마
│   │   └── common.py       # 공통 스키마
│   ├── services/           # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── user.py         # 사용자 서비스
│   │   ├── project.py      # 프로젝트 서비스
│   │   ├── task.py         # 작업 서비스
│   │   └── calendar.py     # 캘린더 서비스
│   ├── utils/              # 유틸리티
│   │   ├── __init__.py
│   │   ├── auth.py         # 인증 유틸리티
│   │   ├── exceptions.py   # 커스텀 예외
│   │   ├── logger.py       # 로깅 설정
│   │   └── helpers.py      # 헬퍼 함수
│   ├── __init__.py
│   └── main.py             # FastAPI 애플리케이션 진입점
├── alembic/                # 데이터베이스 마이그레이션
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── tests/                  # 테스트 코드
├── logs/                   # 로그 파일
├── uploads/                # 업로드 파일
├── .env                    # 환경 변수
├── .env.example            # 환경 변수 예제
├── .gitignore
├── alembic.ini             # Alembic 설정
├── requirements.txt        # Python 의존성
├── Dockerfile              # Docker 이미지 빌드
└── README.md
```

## ⚙️ 환경 설정

### 환경 변수

`.env` 파일에서 다음 환경 변수를 설정하세요:

```bash
# 애플리케이션 설정
PROJECT_NAME=PMS Backend API
VERSION=0.1.0
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# 보안
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 데이터베이스
DATABASE_URL=postgresql+asyncpg://username:password@localhost/pms_db

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8081

# 파일 업로드
MAX_FILE_SIZE=10485760
UPLOAD_PATH=uploads/

# 이메일 (선택사항)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# OAuth (선택사항)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

## 🗄️ 데이터베이스

### 마이그레이션

새로운 마이그레이션 생성:

```bash
alembic revision --autogenerate -m "Add new table"
```

마이그레이션 적용:

```bash
alembic upgrade head
```

마이그레이션 롤백:

```bash
alembic downgrade -1
```

### 초기 데이터

개발용 초기 데이터를 생성하려면:

```bash
python scripts/seed_data.py
```

## 🧪 개발 가이드

### 코드 스타일

프로젝트는 다음 코드 스타일을 따릅니다:

- **PEP 8** 준수
- **Black** 코드 포매터 사용
- **타입 힌팅** 필수
- **독스트링** 작성 권장

코드 포매팅:

```bash
black src/
```

린팅:

```bash
flake8 src/
```

### 테스트

테스트 실행:

```bash
pytest
```

커버리지 확인:

```bash
pytest --cov=src
```

### 새로운 기능 추가

1. **모델 정의** (`models/`에 SQLAlchemy 모델 추가)
2. **스키마 작성** (`schemas/`에 Pydantic 스키마 추가)
3. **서비스 로직** (`services/`에 비즈니스 로직 추가)
4. **API 엔드포인트** (`api/`에 FastAPI 라우터 추가)
5. **테스트 작성** (`tests/`에 테스트 코드 추가)

### 로깅

애플리케이션은 구조화된 로깅을 사용합니다:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("정보 메시지")
logger.error("오류 메시지")
logger.warning("경고 메시지")
```

로그 파일:

- `logs/pms.log` - 일반 로그
- `logs/pms_errors.log` - 오류 로그
- `logs/security.log` - 보안 관련 로그
- `logs/audit.log` - 감사 로그

## 🚀 배포

### Docker 사용

Docker 이미지 빌드:

```bash
docker build -t pms-backend .
```

Docker 컨테이너 실행:

```bash
docker run -p 8000:8000 pms-backend
```

### 프로덕션 배포

프로덕션 환경에서는 다음 사항을 고려하세요:

1. **환경 변수** 설정 (`ENVIRONMENT=production`)
2. **DEBUG** 모드 비활성화 (`DEBUG=false`)
3. **HTTPS** 사용
4. **리버스 프록시** 설정 (Nginx 등)
5. **로그 레벨** 조정 (`LOG_LEVEL=INFO`)
6. **데이터베이스 연결 풀** 설정
7. **보안 헤더** 추가

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 있거나 질문이 있으시면 다음을 통해 연락해 주세요:

- 이슈 트래커: [GitHub Issues](https://github.com/your-repo/issues)
- 이메일: <team@pms.com>

---

**PMS Backend API** - 현대적이고 확장 가능한 프로젝트 관리 시스템
