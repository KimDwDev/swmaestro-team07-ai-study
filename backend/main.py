from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# 테스트 url
@app.get("/api/test")
def home():
    return {"message": "fastapi 테스트"}

# 로드맵 생성 api
class RoadmapRequest(BaseModel): # 로드맵 생성 request 모델
    majorAndYear: str              # 전공/학년
    currentStatus: str             # 현재 상태
    interests: List[str]           # 관심 분야
    targetJob: str                 # 목표 직무
    preferredCompanyType: str      # 희망 회사 유형
    availableTime: str             # 준비 가능 시간
    concerns: List[str]            # 현재 고민

class Roadmap(BaseModel): # 로드맵 모델
    week1To2: List[str]
    week3To4: List[str]
    week5To6: List[str]
    week7To8: List[str]


class RoadmapResponse(BaseModel): # 로드맵 response 모델
    recommendedPath: str
    skillGaps: List[str]
    roadmap: Roadmap

@app.post(
        "/api/users/roadmap",
        response_model=RoadmapResponse
        )
def makeRoadMap(request: RoadmapRequest):
    print("전공 학년: ", request.majorAndYear) 
    print("현재 상태: ", request.currentStatus)
    print("관심 분야: ", request.interests)
    print("목표 직무: ", request.targetJob)
    print("희망 회사 유형: ", request.preferredCompanyType)
    print("준비 가능 시간: ", request.availableTime)
    print("현재 고민: ", request.concerns)

    return RoadmapResponse(
        recommendedPath="백엔드 개발자 로드맵",
        skillGaps=[
            "자료구조와 알고리즘 학습이 필요합니다.",
            "데이터베이스 설계 경험이 부족합니다.",
            "배포 및 운영 경험을 보완하면 좋습니다."
        ],
        roadmap=Roadmap(
            week1To2=[
                "Python 기본 문법 복습",
                "FastAPI 기본 구조 학습",
                "REST API 개념 정리"
            ],
            week3To4=[
                "데이터베이스 연동 학습",
                "SQL 기본 문법 학습",
                "간단한 CRUD API 구현"
            ],
            week5To6=[
                "인증/인가 기능 구현",
                "JWT 기반 로그인 구현",
                "예외 처리 및 유효성 검증 추가"
            ],
            week7To8=[
                "Docker를 이용한 배포 환경 구성",
                "AWS 또는 클라우드 배포 실습",
                "프로젝트 README 정리"
            ]
        )
    )