# 태환님 agent
class Agent2:
  def default(
      self,
      targetJob, # 목표 직무
      preferredCompanyType, # 희망 기업 유형
      maxResults # 검색 공고 수
  ) : # agent 실행 확인 메서드명 변경하셔도 괜찮습니다.
    print("agent2 확인했습니다.")
    
    return {
        # 근거 기업
        "companies": ["sw마에스트로"],

        # 필수 기술
        "required_skills": ["파이썬"],

        # 우대 기술
        "preferred_skills": ["파이썬"],

        # 요구 경험
        "required_experience": ["개발"],

        # 핵심 키워드
        "keywords": ["개발"]
    }