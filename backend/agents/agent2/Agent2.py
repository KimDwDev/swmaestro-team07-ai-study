# 태민님 agent
class Agent2:
  def default( 
      self,
      major, # 전공/학년
      currentStatus, # 현재 상태
      interests, # 관심분야
      ownedSkills, # 사용자 보유 역량 리스트
      targetJob, # 목표 직무
      preferredCompanyType, # 희망 회사 유형
      availableTime, # 준비 가능 기간/주당 시간
      concerns # 현재 고민 (복수 선택 사항)
  ): # agent 실행 확인 메서드명 변경하셔도 괜찮습니다.
    print("agent2 확인했습니다.")
    return {
      # 반환값
     
      # 현재 사용자의 전공, 상태, 고민 등을 종합하여
      # 취업 준비 상태와 배경 맥락을 2~3문장으로 정리
      "summary": "요약",

      # 사용자의 상대적 강점
      "strengths": ["개발"],

      # 목표 직무 대비 보완해야 할 약점
      "weaknesses": ["개발"],

      # strengths, weaknesses 판단 근거
      "evidence": {"개발" : "테스트"}
    }