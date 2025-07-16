import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import json
import random
from datetime import datetime
import tkinter.font as tkfont
from config import APP_WIDTH, APP_HEIGHT, FIREBASE_TEST_MODE, FONT_FAMILY, TITLE_FONT_SIZE, CONTENT_FONT_SIZE
from firebase_manager import FirebaseManager
import traceback
import uuid
import webbrowser  # 웹 브라우저 모듈 추가

# 공통 색상 정의
APP_COLORS = {
    'background': '#FFFFFF',  # 하얀색 배경
    'primary': '#FFB5C5',    # 연한 핑크
    'secondary': '#FFC0CB',  # 밝은 핑크
    'text': '#FFFFFF',      # 텍스트 색상을 하얀색으로 변경
    'white': '#FFFFFF',     # 흰색
    'title': '#FF9AAC',     # 중간 톤의 핑크
    'subtitle': '#FFB5C5',   # 연한 핑크
    'accent': '#FFD1DC',    # 매우 연한 분홍색
    'light_gray': '#F8F9FA', # 연한 회색
    'gray': '#808080',      # 회색
    'dark_gray': '#4A4A4A',  # 어두운 회색
    'matching_bg': '#FFF5F7', # 매칭 화면용 연한 분홍색 배경
    'button': '#FFB5C5',     # 버튼 색상 (연한 핑크)
    'button_hover': '#FF9AAC', # 버튼 호버 색상 (중간 톤의 핑크)
    'result_bg': '#FFF5F7',   # 결과 배경 색상 (연한 핑크)
    'bg': '#FFFFFF'          # 기본 배경 색상
}

def open_instagram_profile(instagram_id):
    """인스타그램 프로필 페이지를 기본 웹 브라우저에서 엽니다."""
    # @ 기호 제거
    clean_id = instagram_id.replace('@', '')
    # 인스타그램 프로필 URL 생성
    url = f"https://instagram.com/{clean_id}"
    # 기본 웹 브라우저에서 URL 열기
    webbrowser.open(url)

class MBTITest:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        self.colors = APP_COLORS
        
        self.root.configure(bg=self.colors['background'])
        
        # 질문과 답변 설정
        self.questions = [
            {
                'question': '시험이 끝난 후 귀사하였다.\n기숙사에 왔을 때 나는?',
                'answers': [
                    '시험도 끝났는데 놀아야지!!\n애들 방으로 놀러가야지~~',
                    '애들이랑 노는 것도 좋지만\n오늘은 혼자 쉬어야지 침대와 몰아일체!'
                ],
                'types': ['E', 'I']
            },
            {
                'question': '기숙사 방을 옮기고\n새로 세팅을 할 때 나는?',
                'answers': [
                    '있는 그대로 사용한다.\n필요한 거만 쓰면 되지',
                    '나만의 취향과 생활습관에 맞춰서\n효율적으로 세팅해야지.'
                ],
                'types': ['S', 'N']
            },
            {
                'question': '친구가 시험을 망쳤다고\n울고 있다. 이때 나는?',
                'answers': [
                    '속상했겠다ㅠㅠ\n다음엔 더 잘할 수 있을거야!!',
                    '너가 더 노력하면 다음에 더 잘되겠지\n일단 에쏠부터 가자'
                ],
                'types': ['F', 'T']
            },
            {
                'question': '시험 일주일 전!!\n이때 나의 상태는?',
                'answers': [
                    '한건 많은 것 같은데\n플래너는 텅 비었음..',
                    '내일 플래너까지 세워져 있고\n앞으로의 계획이 완벽!!'
                ],
                'types': ['P', 'J']
            }
        ]
        
        self.mbti_descriptions = {
            'ENFP': '능주 핵인싸, 기숙사 복도만 걸어도 친구생김',
            'ENTP': '공부하다가 창업 아이템 생각해냄',
            'ESFP': '쉬는 시간 = 복도 런웨이',
            'ESTP': '공부? 일단 이것만 보고',
            'INFP': '계획은 잘 세움, 실천은 내일',
            'INFJ': '조용한데 친해지면 투머치토커',
            'ISFP': '방 꾸미기에 진심, 자기 혼자 인스타 감성',
            'ISTP': '무심한 해결사, 기숙사 맥가이버',
            'INTP': '단어 외우다가 존재 이유에 대해 고민함',
            'INTJ': '시험계획은 3주 전에 완성, 실천도 함',
            'ISTJ': '매일 같은 루틴으로 삶, 루틴 깨지면 멘붕',
            'ESTJ': '자습 때 말하는 애들이 세상에서 제일 싫음',
            'ENFJ': '기숙사 엄마상, 찾았다 우리엄마',
            'ESFJ': '우리 반 분위기는 내가 책임진다.',
            'ISFJ': '쟤 청소 진짜 열심히 한다. 에서 쟤',
            'ENTJ': '실행력 10000%'
        }
        
        self.current_question = 0
        self.answers = []
        
        self.create_welcome_screen()
        
    def create_welcome_screen(self):
        # 시작 화면 프레임
        welcome_frame = ctk.CTkFrame(self.root, fg_color=self.colors['background'])
        welcome_frame.pack(fill="both", expand=True)
        
        # 제목
        title = ctk.CTkLabel(
            welcome_frame, 
            text="MBTI 검사",
            font=("Pretendard", 32, "bold"),
            text_color=self.colors['dark_gray']  # 검정색으로 변경
        )
        title.pack(pady=20)
        
        # 시작 버튼
        start_button = ctk.CTkButton(
            welcome_frame,
            text="검사 시작하기",
            font=("Pretendard", 16),
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            text_color=self.colors['white'],
            command=self.start_test
        )
        start_button.pack(pady=20)
        
    def start_test(self):
        self.show_question()
        
    def show_question(self):
        # 기존 위젯 제거
        for widget in self.root.winfo_children():
            widget.destroy()
            
        if self.current_question >= len(self.questions):
            self.show_result()
            return
            
        question = self.questions[self.current_question]
        
        # 메인 프레임
        main_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['background'],
            corner_radius=20
        )
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # 진행 상황 표시
        progress_text = f"Question {self.current_question + 1}/{len(self.questions)}"
        progress_label = ctk.CTkLabel(
            main_frame,
            text=progress_text,
            font=("Pretendard", 20),
            text_color=self.colors['dark_gray']  # 검정색으로 변경
        )
        progress_label.pack(pady=(20, 10))
        
        # 질문 텍스트
        question_label = ctk.CTkLabel(
            main_frame,
            text=question['question'],
            font=("Pretendard", 28, "bold"),
            text_color=self.colors["dark_gray"]  # 검정색으로 변경
        )
        question_label.pack(pady=(20, 40))
        
        # 답변 버튼들을 위한 프레임
        answers_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        answers_frame.pack(fill="x", padx=40, pady=20)
        
        # 답변 버튼들
        for i, answer in enumerate(question['answers']):
            # 답변 버튼
            btn = ctk.CTkButton(
                answers_frame,
                text=answer,
                font=("Pretendard", 18),
                fg_color=self.colors['button'],
                hover_color=self.colors['button_hover'],
                text_color=self.colors['white'],
                width=700,
                height=120,
                corner_radius=15,
                command=lambda x=i: self.answer_selected(x)
            )
            btn.pack(pady=15)
        
    def answer_selected(self, answer_index):
        question = self.questions[self.current_question]
        self.answers.append(question['types'][answer_index])
        self.current_question += 1
        self.show_question()
        
    def show_result(self):
        # 기존 위젯 제거
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # MBTI 결과 계산
        mbti = ''.join(self.answers)
        description = self.mbti_descriptions.get(mbti, "알 수 없는 유형")
        
        # 결과 프레임
        result_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["white"],  # 하얀색 배경으로 변경
            corner_radius=15
        )
        result_frame.pack(fill="x", padx=20, pady=10)
        
        # MBTI 결과
        mbti_label = ctk.CTkLabel(
            result_frame,
            text=mbti,
            font=("Pretendard", 48, "bold"),
            text_color=self.colors["title"]  # 핑크색 유지
        )
        mbti_label.pack(pady=(60, 30))
        
        # 설명
        desc_label = ctk.CTkLabel(
            result_frame,
            text=description,
            font=("Pretendard", 24),
            wraplength=600,
            text_color=self.colors["dark_gray"]  # 검은색으로 변경
        )
        desc_label.pack(pady=40)
        
        # 확인 버튼
        confirm_button = ctk.CTkButton(
            result_frame,
            text="결과 확인",
            font=("Pretendard", 20),
            fg_color=self.colors['button'],
            hover_color=self.colors['button'],
            text_color=self.colors['white'],
            width=200,
            height=50,
            corner_radius=25,
            command=lambda: self.confirm_result(confirm_button, mbti)
        )
        confirm_button.pack(pady=40)

    def confirm_result(self, button, mbti):
        """결과 확인 버튼 클릭 처리"""
        # 버튼 비활성화 및 텍스트 변경
        button.configure(
            state="disabled",
            text="✓ 결과 확인 완료",
            fg_color=["#2ecc71", "#27ae60"]  # 초록색 계열
        )
        # 콜백 함수 호출
        self.callback(mbti)

class StudentMatchingApp:
    def __init__(self, root):
        self.root = root
        self.current_student = None
        self.colors = APP_COLORS
        self.matching_attempts = 0
        
        # MBTI 궁합 정보 추가
        self.mbti_compatibility = {
            'ENFP': ['INFJ', 'INTJ'],
            'INFJ': ['ENFP', 'ENTP'],
            'ENFJ': ['INFP', 'ISFP'],
            'INFP': ['ENFJ', 'ENTJ'],
            'ENTP': ['INFJ', 'INTJ'],
            'INTP': ['ENTJ', 'ESTJ'],
            'ENFJ': ['INFP', 'ISFP'],
            'ENTJ': ['INFP', 'INTP'],
            'ESFP': ['ISFJ', 'ISTJ'],
            'ISFP': ['ENFJ', 'ESFJ'],
            'ESTP': ['ISFJ', 'ISTJ'],
            'ISTP': ['ESFJ', 'ESTJ'],
            'ESFJ': ['ISFP', 'ISTP'],
            'ISFJ': ['ESFP', 'ESTP'],
            'ESTJ': ['ISTP', 'INTP'],
            'ISTJ': ['ESFP', 'ESTP']
        }
        
        # 기본 폰트 설정
        self.title_font = ("Pretendard", 24, "bold")
        self.content_font = ("Pretendard", 14)
        
        # Firebase 초기화
        try:
            self.firebase_manager = FirebaseManager()
            print("StudentMatchingApp Firebase 초기화 완료")
        except Exception as e:
            print(f"StudentMatchingApp Firebase 초기화 오류: {str(e)}")
            messagebox.showerror("오류", "매칭 시스템 초기화 중 오류가 발생했습니다.")
        
    def initialize(self, student_data):
        """앱 초기화"""
        try:
            print("초기화 시작:", student_data)
            self.current_student = student_data
            
            # 학년 데이터 처리
            grade = student_data.get('grade')
            if isinstance(grade, str):
                grade = int(grade.replace('학년', ''))
            
            # user_id가 이미 있다면 기존 사용자이므로 저장하지 않음
            if not student_data.get('user_id'):
                # 새로운 사용자의 경우에만 Firebase에 저장
                profile_data = {
                    'nickname': student_data.get('name', ''),
                    'name': student_data.get('name', ''),
                    'grade': grade,
                    'instagram': student_data.get('instagram', '').replace('@', ''),
                    'mbti': student_data.get('mbti', ''),
                    'gender': student_data.get('gender', ''),
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'last_reset_date': datetime.now().strftime("%Y-%m-%d")
                }
                
                print("저장할 프로필 데이터:", profile_data)
                
                # Firebase에 프로필 저장
                user_id = self.firebase_manager.save_profile(profile_data)
                if user_id:
                    self.current_student['user_id'] = user_id
                    print(f"프로필 저장 완료 (ID: {user_id})")
                else:
                    print("프로필 저장 실패")
                    raise Exception("프로필 저장에 실패했습니다.")
            
            # 오늘의 매칭 시도 횟수 확인 및 리셋
            today = datetime.now().strftime("%Y-%m-%d")
            current_id = student_data.get('user_id')
            if current_id:
                # 마지막 리셋 날짜 확인
                last_reset_date = self.firebase_manager.get_last_reset_date(current_id)
                if last_reset_date != today:
                    # 날짜가 변경되었으면 매칭 횟수 리셋
                    self.firebase_manager.reset_matching_attempts(current_id, today)
                    self.matching_attempts = 0
                else:
                    self.matching_attempts = self.firebase_manager.get_matching_attempts(current_id, today)
                print(f"오늘의 매칭 시도 횟수: {self.matching_attempts}")
            else:
                print("사용자 ID를 찾을 수 없습니다.")
                raise Exception("사용자 ID를 찾을 수 없습니다.")
            
            self.create_widgets()
            
        except Exception as e:
            print(f"초기화 중 오류 발생: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("오류", f"매칭 시스템 초기화 중 오류가 발생했습니다.\n{str(e)}")

    def create_widgets(self):
        """UI 위젯 생성"""
        # 메인 컨테이너
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["bg"],
            corner_radius=20
        )
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 제목
        title = ctk.CTkLabel(
            self.main_frame, 
            text="능주고등학교 친구 찾기",
            font=("Pretendard", 24, "bold"),
            text_color=self.colors["primary"]
        )
        title.pack(pady=20)
        
        # 현재 학생 정보 카드
        self.create_profile_card()
        
        # 학년 선택 섹션
        self.create_grade_selection()
        
        # 매칭 버튼
        self.create_matching_button()
        
        # 매칭 결과 영역
        self.create_result_section()

    def create_matching_button(self):
        """매칭 버튼 생성"""
        # 남은 매칭 횟수 표시 레이블
        self.attempts_label = ctk.CTkLabel(
            self.main_frame,
            text=f"남은 매칭 횟수: {5 - self.matching_attempts}회",
            font=("Pretendard", 16),
            text_color=self.colors['text']
        )
        self.attempts_label.pack(pady=(0, 10))

        # 매칭 버튼
        self.match_button = ctk.CTkButton(
            self.main_frame,
            text="랜덤 매칭 시작",
            font=("Pretendard", 16, "bold"),
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            text_color=self.colors['white'],
            corner_radius=30,
            width=250,
            height=50,
            command=self.start_matching
        )
        
        # 매칭 횟수가 5회 이상이면 버튼 비활성화
        if self.matching_attempts >= 5:
            self.match_button.configure(
                state="disabled",
                fg_color=self.colors['gray'],
                text="오늘의 매칭 완료"
            )
        
        self.match_button.pack(pady=10)

    def create_result_section(self):
        """매칭 결과 섹션 생성"""
        self.result_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["white"],
            corner_radius=15,
            height=300  # 높이를 300으로 증가
        )
        self.result_frame.pack(fill="x", padx=20, pady=10)
        self.result_frame.pack_propagate(False)
        
        # 결과 섹션 제목
        result_title = ctk.CTkLabel(
            self.result_frame,
            text="매칭 결과",
            font=("Pretendard", 20, "bold"),
            text_color=self.colors["white"]
        )
        result_title.pack(pady=(20, 15))
        
        # 결과 표시 영역 수정
        # 결과 프레임 생성
        result_container = ctk.CTkFrame(
            self.result_frame,
            fg_color="transparent",
            border_color=self.colors["title"],  # 진한 핑크색 테두리
            border_width=2,
            corner_radius=10
        )
        result_container.pack(pady=(10, 20), padx=20, fill="x")

        # 결과 제목
        result_title = ctk.CTkLabel(
            result_container,
            text="매칭 결과",
            font=("Pretendard", 16, "bold"),
            text_color=self.colors["dark_gray"]  # 진한 글씨
        )
        result_title.pack(pady=(15, 5))

        # 결과 내용
        self.result_label = ctk.CTkLabel(
            result_container,
            text="매칭된 친구를 찾고 있습니다...",
            font=("Pretendard", 14),
            text_color=self.colors["dark_gray"],
            wraplength=500
        )
        self.result_label.pack(pady=(5, 15))

    def start_matching(self):
        """매칭 시작"""
        try:
            # 현재 사용자 ID 확인
            current_id = self.current_student.get('user_id')
            if not current_id:
                raise Exception("현재 사용자 ID를 찾을 수 없습니다.")

            # 오늘 날짜의 매칭 시도 횟수 다시 확인
            today = datetime.now().strftime("%Y-%m-%d")
            self.matching_attempts = self.firebase_manager.get_matching_attempts(current_id, today)
            
            # 매칭 횟수 초과 확인
            if self.matching_attempts >= 5:
                messagebox.showwarning(
                    "매칭 제한",
                    "오늘의 매칭 횟수를 모두 사용했습니다.\n내일 다시 시도해주세요!"
                )
                return
                
            # 매칭 시작 전 알림 (남은 횟수 표시)
            if not messagebox.askokcancel(
                "매칭 시작",
                f"매칭을 시작합니다!\n\n" +
                f"오늘 남은 매칭 횟수: {5 - self.matching_attempts}회\n\n" +
                "MBTI 궁합을 우선으로 매칭을 시도합니다.\n" +
                "적절한 매칭이 없으면 랜덤으로 매칭됩니다.\n\n" +
                "계속하시겠습니까?"
            ):
                return

            # 매칭 파라미터 설정
            current_instagram = self.current_student.get('instagram', '').replace('@', '')
            current_mbti = self.current_student.get('mbti', '')
            target_grade = None
            
            if hasattr(self, 'target_grade') and self.target_grade != "전체":
                target_grade = int(self.target_grade[0])

            # MBTI 궁합이 맞는 유형들
            compatible_mbti_types = self.mbti_compatibility.get(current_mbti, [])
            
            # Firebase에서 직접 필터링된 사용자 가져오기
            matched_student = self.firebase_manager.get_filtered_users(
                current_id=current_id,
                current_instagram=current_instagram,
                target_grade=target_grade,
                compatible_mbti_types=compatible_mbti_types
            )
            
            if not matched_student:
                messagebox.showinfo(
                    "알림", 
                    "매칭 가능한 학생이 없습니다.\n다른 학년을 선택해보세요!"
                )
                return
                
            student_grade = matched_student.get('grade')
            if isinstance(student_grade, str):
                student_grade = student_grade.replace('학년', '')
                
            # 매칭 결과 표시
            match_type = "MBTI 궁합" if matched_student.get('mbti') in compatible_mbti_types else "랜덤"
            result_text = f"""
매칭된 친구 정보 ({match_type})

별명: {matched_student.get('nickname', '알 수 없음')}
학년: {student_grade}학년
성별: {matched_student.get('gender', '알 수 없음')}
MBTI: {matched_student.get('mbti', '알 수 없음')}
            """
            self.result_label.configure(
                text=result_text,
                justify="left"
            )
            
            # 친구 요청 확인 창
            if messagebox.askyesno(
                "친구 요청 확인",
                f"이 친구에게 친구 요청을 보내시겠습니까?\n\n{result_text}",
                icon="question"
            ):
                # 친구 요청 알림 저장
                if self.firebase_manager.save_friend_request(
                    self.current_student['user_id'],
                    matched_student['user_id'],
                    self.current_student.get('nickname', '알 수 없음'),
                    self.current_student.get('instagram', '')
                ):
                    messagebox.showinfo(
                        "성공", 
                        f"{matched_student.get('nickname', '알 수 없음')} 학생에게\n친구 요청을 보냈습니다!\n\n상대방의 수락을 기다려주세요."
                    )
                else:
                    raise Exception("친구 요청 저장에 실패했습니다.")
            else:
                # 거절 시 결과 텍스트 초기화
                self.result_label.configure(
                    text="매칭된 친구를 찾고 있습니다...",
                    justify="center"
                )
                
            # 매칭 시도 횟수 증가 및 저장
            if self.firebase_manager.increment_matching_attempts(current_id, today):
                print(f"매칭 시도 횟수 증가 성공 (현재: {self.matching_attempts + 1})")
                self.matching_attempts += 1
                self.attempts_label.configure(text=f"남은 매칭 횟수: {5 - self.matching_attempts}회")
                
                # 매칭 횟수가 5회가 되면 버튼 비활성화
                if self.matching_attempts >= 5:
                    self.match_button.configure(
                        state="disabled",
                        fg_color=self.colors['gray'],
                        text="오늘의 매칭 완료"
                    )
                
                # 매칭 화면 새로고침 (수락한 경우에만)
                if messagebox.askyesno:
                    self.show_home_screen()
            else:
                raise Exception("매칭 시도 횟수 증가 실패")
                
        except Exception as e:
            print(f"매칭 중 오류 발생: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("오류", f"매칭 처리 중 오류가 발생했습니다.\n{str(e)}")

    def create_grade_selection(self):
        """학년 선택 섹션 생성"""
        grade_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["white"],
            corner_radius=15
        )
        grade_frame.pack(fill="x", padx=20, pady=10)
        
        # 학년 선택 제목
        grade_title = ctk.CTkLabel(
            grade_frame,
            text="매칭 학년 선택",
            font=("Pretendard", 16, "bold"),
            text_color=self.colors["primary"]
        )
        grade_title.pack(pady=(15, 10))
        
        # 콤보박스 생성
        self.grade_var = tk.StringVar(value="전체")
        grade_combo = ttk.Combobox(
            grade_frame,
            textvariable=self.grade_var,
            values=["전체", "1학년", "2학년", "3학년"],
            state="readonly",
            width=15,
            font=self.content_font
        )
        grade_combo.pack(pady=(0, 15))
        grade_combo.bind('<<ComboboxSelected>>', self.on_grade_selected)

    def on_grade_selected(self, event):
        """학년 선택 시 호출되는 콜백"""
        self.target_grade = self.grade_var.get()

    def create_profile_card(self):
        """프로필 카드 생성"""
        profile_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["secondary"],
            corner_radius=15
        )
        profile_frame.pack(fill="x", padx=20, pady=10)
        
        # 프로필 제목
        profile_title = ctk.CTkLabel(
            profile_frame,
            text="내 정보",
            font=("Pretendard", 18, "bold"),
            text_color=self.colors["white"]
        )
        profile_title.pack(pady=(15, 10))
        
        # 프로필 정보
        info_text = f"""
인스타그램: {self.current_student.get('instagram', '')}
학년: {self.current_student.get('grade', '')}학년
MBTI: {self.current_student.get('mbti', '')}
성별: {self.current_student.get('gender', '')}
        """
        
        profile_label = ctk.CTkLabel(
            profile_frame,
            text=info_text,
            font=("Pretendard", 14),
            text_color=self.colors["white"]
        )
        profile_label.pack(pady=(0, 15))

    def update_requests_list(self):
        """받은 요청 목록 업데이트"""
        # 기존 위젯 제거
        for widget in self.requests_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):  # 제목 라벨 제외
                widget.destroy()
        
        # 현재 학생이 받은 요청 필터링 (대기 중인 요청만)
        received_requests = [
            r for r in self.matching_requests 
            if r['receiver_id'] == self.current_student['user_id'] and 
            r['status'] == "pending"
        ]
        
        if not received_requests:
            no_requests_label = ctk.CTkLabel(
                self.requests_frame,
                text="💌 새로운 매칭 요청이 없습니다",
                font=("Pretendard", 14),
                text_color=self.colors["text"]
            )
            no_requests_label.pack(pady=(0, 15))
            return
            
        # 요청 목록 표시
        for request in received_requests:
            self.create_request_item(request)
            
    def create_request_item(self, request):
        """요청 아이템 UI 생성"""
        item_frame = ctk.CTkFrame(
            self.requests_frame,
            fg_color=self.colors["bg"],
            corner_radius=10
        )
        item_frame.pack(fill="x", padx=15, pady=5)
        
        # 요청 정보 표시
        sender = next((s for s in self.students if s['user_id'] == request['sender_id']), None)
        if sender:
            info_text = f"""
📨 {sender['nickname']}님의 매칭 요청
📚 {sender['grade']}학년 {sender['class']}반
💝 관심사: {', '.join(sender['interests'])}
            """
        else:
            info_text = f"📨 {request['sender_name']}님의 매칭 요청"
            
        info_label = ctk.CTkLabel(
            item_frame,
            text=info_text,
            font=("Pretendard", 14),
            text_color=self.colors["text"]
        )
        info_label.pack(side="left", padx=15, pady=10)
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(
            item_frame,
            fg_color="transparent"
        )
        button_frame.pack(side="right", padx=15, pady=10)
        
        # 수락 버튼
        accept_button = ctk.CTkButton(
            button_frame,
            text="✅ 수락",
            font=("Pretendard", 14),
            fg_color=self.colors["accent"],
            text_color=self.colors["text"],
            width=80,
            height=30,
            corner_radius=15,
            command=lambda m=request: self.handle_request(m, 'accepted')
        )
        accept_button.pack(side="left", padx=5)
        
        # 거절 버튼
        reject_button = ctk.CTkButton(
            button_frame,
            text="❌ 거절",
            font=("Pretendard", 14),
            fg_color=self.colors["secondary"],
            text_color=self.colors["text"],
            width=80,
            height=30,
            corner_radius=15,
            command=lambda m=request: self.handle_request(m, 'rejected')
        )
        reject_button.pack(side="left", padx=5)
        
    def handle_request(self, request, status):
        """요청 처리"""
        request['status'] = status
        
        # Firebase/로컬 저장소에 상태 업데이트
        self.firebase_manager.update_matching(request)
        
        # Firebase에서 직접 발신자 정보 조회
        sender_name = request.get('sender_nickname', '알 수 없음')
        
        if status == "accepted":
            messagebox.showinfo(
                "매칭 수락", 
                f"✨ {sender_name} 학생과의 매칭이 성사되었습니다!\n\n" +
                "서로 존중하고 배려하는 멋진 친구 관계가 되길 바랍니다. 💝"
            )
        else:
            messagebox.showinfo(
                "매칭 거절", 
                f"😢 {sender_name} 학생과의 매칭을 거절했습니다."
            )
            
        # 요청 목록 업데이트
        self.update_requests_list()

    def on_mbti_result(self, mbti_result):
        """MBTI 테스트 결과 처리"""
        try:
            # 프로필 정보에 MBTI 결과 추가
            self.temp_profile['mbti'] = mbti_result
            
            # Firebase에 저장할 데이터 준비
            profile_data = {
                'gender': self.temp_profile['gender'],
                'grade': self.temp_profile['grade'].replace('학년', ''),  # '1학년' -> '1'
                'nickname': self.temp_profile['nickname'],
                'instagram': self.temp_profile['instagram'].replace('@', ''),  # @ 제거
                'mbti': self.temp_profile['mbti'],
                'name': self.temp_profile['name'],
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print("Firebase에 저장할 프로필 데이터:", profile_data)  # 디버깅 로그
            
            # Firebase에 프로필 저장
            try:
                user_id = self.firebase_manager.save_profile(profile_data)
                if user_id:
                    print(f"Firebase에 프로필 저장 성공 (ID: {user_id})")  # 디버깅 로그
                    
                    # 프로필 데이터 설정
                    self.profile_data = {
                        'user_id': user_id,
                        'nickname': profile_data['nickname'],
                        'instagram': profile_data['instagram'],
                        'grade': profile_data['grade'],
                        'gender': profile_data['gender'],
                        'mbti': profile_data['mbti'],
                        'name': profile_data['name']
                    }
                    
                    messagebox.showinfo("성공", "프로필이 저장되었습니다!")
                    self.show_home_screen()
                else:
                    raise Exception("Firebase 저장 실패: user_id가 반환되지 않음")
            except Exception as e:
                print(f"Firebase 저장 오류: {str(e)}")  # 디버깅 로그
                raise Exception(f"Firebase 저장 실패: {str(e)}")
        except Exception as e:
            error_msg = f"프로필 저장 중 오류가 발생했습니다: {str(e)}"
            print(error_msg)  # 디버깅 로그
            messagebox.showerror("오류", error_msg)
            print("Error details:", e)  # 디버깅 로그

    def run(self):
        self.root.mainloop()

    def show_home_screen(self):
        """매칭 화면 새로고침"""
        try:
            # 기존 위젯 제거
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # 현재 매칭 시도 횟수 다시 확인
            today = datetime.now().strftime("%Y-%m-%d")
            current_id = self.current_student.get('user_id')
            if current_id:
                self.matching_attempts = self.firebase_manager.get_matching_attempts(current_id, today)
            
            # UI 재생성
            self.create_widgets()
            
        except Exception as e:
            print(f"화면 새로고침 중 오류 발생: {str(e)}")
            messagebox.showerror("오류", "화면을 새로고침하는 중 오류가 발생했습니다.")

class FriendFinderApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🌸 능친 만들기 🌸")
        self.root.geometry("800x600")
        
        # 색상 테마 설정
        self.colors = APP_COLORS
        
        # Firebase 매니저 초기화
        self.firebase_manager = FirebaseManager()
        self.profile_data = None
        
        self.root.configure(fg_color=self.colors['background'])
        self.show_initial_screen()
        
    def show_initial_screen(self):
        # 기존 위젯들 제거
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 시작 화면 프레임
        self.start_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors['white']
        )
        self.start_frame.pack(fill="both", expand=True)
        
        # 메인 타이틀
        title = ctk.CTkLabel(
            self.start_frame,
            text="능친 만들기",
            font=("Pretendard", 52, "bold"),
            text_color=self.colors['title']
        )
        title.pack(pady=(120, 40))
        
        # 부제목
        subtitle = ctk.CTkLabel(
            self.start_frame,
            text="당신의 특별한 인연을 찾아보세요",
            font=("Pretendard", 24),
            text_color=self.colors['subtitle']
        )
        subtitle.pack(pady=20)
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(
            self.start_frame,
            fg_color="transparent"
        )
        button_frame.pack(pady=60)
        
        # START 버튼
        start_button = ctk.CTkButton(
            button_frame,
            text="START",
            font=("Pretendard", 32, "bold"),
            fg_color="#FF9AAC",  # 처음부터 진한 핑크
            hover_color="#FF9AAC",  # hover 효과 제거
            text_color=self.colors['white'],
            width=300,
            height=80,
            corner_radius=40,
            command=self.show_login_options
        )
        start_button.pack()
        
        # 하단 장식
        decoration2 = ctk.CTkLabel(
            self.start_frame,
            text="✧･ﾟ: *✧･ﾟ:* ♡ *:･ﾟ✧*:･ﾟ✧",
            font=("Pretendard", 24),
            text_color=self.colors['primary']
        )
        decoration2.pack(pady=20)
        
    def is_valid_mbti(self, mbti):
        """MBTI 유효성 검사"""
        if len(mbti) != 4:
            return False
            
        valid_chars = {
            0: {'E', 'I'},
            1: {'N', 'S'},
            2: {'F', 'T'},
            3: {'J', 'P'}
        }
        
        for i, char in enumerate(mbti):
            if char not in valid_chars[i]:
                return False
        return True
        
    def show_login_options(self):
        """START 버튼 클릭 시 로그인 옵션 화면 표시"""
        # 기존 위젯들 제거
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 메인 프레임
        main_frame = ctk.CTkFrame(self.root, fg_color=self.colors["white"])
        main_frame.pack(fill="both", expand=True)
        
        # 타이틀
        title = ctk.CTkLabel(
            main_frame,
            text="💝 능친 만들기 💝",
            font=("Pretendard", 28, "bold"),
            text_color="#FF1493"  # 밝은 핫핑크
        )
        title.pack(pady=(100, 50))
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # 기존 프로필로 로그인 버튼
        login_button = ctk.CTkButton(
            button_frame,
            text="기존 프로필로 로그인",
            font=("Pretendard", 16),
            fg_color="#FF9AAC",
            hover_color="#FF9AAC",
            text_color="#FFFFFF",
            width=250,
            height=50,
            corner_radius=25,
            command=self.show_login_screen
        )
        login_button.pack(pady=10)
        
        # 새 프로필 만들기 버튼
        new_profile_button = ctk.CTkButton(
            button_frame,
            text="새 프로필 만들기",
            font=("Pretendard", 16),
            fg_color="transparent",
            hover_color="#FF9AAC",
            text_color="#FF9AAC",
            border_color="#FF9AAC",
            border_width=2,
            width=250,
            height=50,
            corner_radius=25,
            command=self.show_privacy_consent
        )
        new_profile_button.pack(pady=10)
        
    def show_login_screen(self):
        """기존 프로필로 로그인 화면 표시"""
        # 기존 위젯들 제거
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 메인 프레임
        main_frame = ctk.CTkFrame(self.root, fg_color=self.colors['white'])
        main_frame.pack(fill="both", expand=True)
        
        # 타이틀
        title = ctk.CTkLabel(
            main_frame,
            text="프로필 로그인",
            font=("Pretendard", 28, "bold"),
            text_color=self.colors['title']
        )
        title.pack(pady=(80, 50))
        
        # 입력 필드 프레임
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(pady=20)
        
        # 이름 입력
        name_label = ctk.CTkLabel(
            input_frame,
            text="이름",
            font=("Pretendard", 14),
            text_color=self.colors['text']
        )
        name_label.pack(pady=(0, 5))
        
        self.login_name_entry = ctk.CTkEntry(
            input_frame,
            width=250,
            height=40,
            font=("Pretendard", 14),
            placeholder_text="본인 이름 입력"
        )
        self.login_name_entry.pack(pady=(0, 15))

        # 별명 입력
        nickname_label = ctk.CTkLabel(
            input_frame,
            text="별명",
            font=("Pretendard", 14),
            text_color=self.colors['text']
        )
        nickname_label.pack(pady=(0, 5))
        
        self.login_nickname_entry = ctk.CTkEntry(
            input_frame,
            width=250,
            height=40,
            font=("Pretendard", 14),
            placeholder_text="기존 별명 입력"
        )
        self.login_nickname_entry.pack(pady=(0, 15))
        
        # 인스타그램 아이디 입력
        insta_label = ctk.CTkLabel(
            input_frame,
            text="인스타그램 아이디",
            font=("Pretendard", 14),
            text_color=self.colors['text']
        )
        insta_label.pack(pady=(0, 5))
        
        self.login_insta_entry = ctk.CTkEntry(
            input_frame,
            width=250,
            height=40,
            font=("Pretendard", 14),
            placeholder_text="@아이디"
        )
        self.login_insta_entry.pack(pady=(0, 5))
        self.login_insta_entry.insert(0, '@')  # 초기값으로 @ 설정
        
        # 인스타그램 아이디 안내 문구
        insta_guide = ctk.CTkLabel(
            input_frame,
            text="✨ 인스타그램 아이디를 입력해주세요",
            font=("Pretendard", 12),
            text_color=self.colors['subtitle']  # 연한 핑크색
        )
        insta_guide.pack(pady=(0, 15))
        
        # 입력 내용이 변경될 때마다 호출되는 함수
        def on_insta_change(event=None):
            current_text = self.login_insta_entry.get()
            cursor_position = self.login_insta_entry.index(tk.INSERT)
            
            if not current_text.startswith('@'):
                self.login_insta_entry.delete(0, tk.END)
                self.login_insta_entry.insert(0, '@' + current_text.replace('@', ''))
                self.login_insta_entry.icursor(cursor_position + 1)
            
            if current_text == '@':
                self.login_insta_entry.icursor(1)
                
        self.login_insta_entry.bind('<KeyRelease>', on_insta_change)
        
        # 백스페이스로 @ 삭제 방지
        def prevent_at_deletion(event):
            if event.keysym == 'BackSpace' and self.login_insta_entry.index(tk.INSERT) <= 1:
                return 'break'
            
        self.login_insta_entry.bind('<Key>', prevent_at_deletion)
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # 로그인 버튼
        login_button = ctk.CTkButton(
            button_frame,
            text="로그인",
            font=("Pretendard", 16),
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            text_color=self.colors['white'],
            width=250,
            height=45,
            corner_radius=25,
            command=self.verify_login
        )
        login_button.pack(pady=10)
        
        # 뒤로가기 버튼
        back_button = ctk.CTkButton(
            button_frame,
            text="← 뒤로가기",
            font=("Pretendard", 14),
            fg_color='transparent',
            hover_color="#FF9AAC",
            text_color="#FF9AAC",
            border_color="#FF9AAC",
            border_width=2,
            width=250,
            height=45,
            corner_radius=25,
            command=self.show_login_options
        )
        back_button.pack(pady=10)
        
    def verify_login(self):
        """로그인 정보 확인"""
        try:
            print("\n=== 로그인 시도 ===")
            
            # 입력값 검증
            nickname = self.login_nickname_entry.get().strip()
            instagram = self.login_insta_entry.get().strip().replace('@', '')
            name = self.login_name_entry.get().strip()
            
            print(f"입력된 정보:")
            print(f"- 별명: '{nickname}'")
            print(f"- 인스타그램: '{instagram}'")
            print(f"- 이름: '{name}'")
            
            # 입력값 유효성 검사
            if not nickname or not instagram:
                print("오류: 필수 필드 누락")
                messagebox.showerror("오류", "별명과 인스타그램 아이디를 입력해주세요.")
                return
                
            if not instagram or instagram == '@':
                print("오류: 인스타그램 아이디 누락")
                messagebox.showerror("오류", "올바른 인스타그램 아이디를 입력해주세요.")
                return
            
            try:
                print("\nFirebase 사용자 조회 시작...")
                # Firebase에서 사용자 정보 확인 (대소문자 구분 없이)
                user = self.firebase_manager.get_user_by_credentials(
                    nickname=nickname,
                    instagram=instagram,
                    name=name  # 이름은 전달하지만 검증에는 사용하지 않음
                )
                
                if user:
                    print("\n사용자 찾음, 프로필 데이터 설정 중...")
                    # 프로필 데이터 설정
                    self.profile_data = {
                        'user_id': user.get('user_id'),
                        'nickname': user.get('nickname'),
                        'instagram': user.get('instagram'),
                        'grade': user.get('grade'),
                        'gender': user.get('gender'),
                        'mbti': user.get('mbti'),
                        'name': user.get('name')
                    }
                    
                    print(f"설정된 프로필 데이터: {self.profile_data}")
                    
                    # 필수 필드 확인
                    missing_fields = [field for field, value in self.profile_data.items() 
                                   if not value and field != 'mbti']
                    if missing_fields:
                        print(f"오류: 불완전한 프로필 - 누락된 필드: {missing_fields}")
                        raise Exception(f"프로필 정보가 불완전합니다: {', '.join(missing_fields)}")
                    
                    print("\n로그인 성공!")
                    messagebox.showinfo("성공", "로그인되었습니다!")
                    self.show_home_screen()
                else:
                    print("\n오류: 일치하는 사용자 없음")
                    messagebox.showerror(
                        "오류", 
                        "일치하는 프로필을 찾을 수 없습니다.\n" +
                        "별명과 인스타그램 아이디를 다시 확인해주세요."
                    )
                    
            except Exception as e:
                print(f"\nFirebase 데이터 조회 중 오류: {str(e)}")
                traceback.print_exc()
                raise Exception(f"데이터베이스 오류: {str(e)}")
                
        except Exception as e:
            print(f"\n로그인 처리 중 오류 발생: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("오류", f"로그인 처리 중 오류가 발생했습니다.\n{str(e)}")

    def show_home_screen(self):
        # 기존 위젯들 제거
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 메인 프레임
        main_frame = ctk.CTkFrame(self.root, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 상단 프로필 카드
        profile_card = ctk.CTkFrame(
            main_frame,
            fg_color="#FFB6C1",  # 연한 분홍색
            corner_radius=15
        )
        profile_card.pack(fill="x", padx=20, pady=20)
        
        # 환영 메시지
        welcome_text = f"✨ 환영합니다! ✨"
        welcome_label = ctk.CTkLabel(
            profile_card,
            text=welcome_text,
            font=("Pretendard", 24, "bold"),
            text_color=self.colors["white"]
        )
        welcome_label.pack(pady=(20, 5))
        
        # 이름 정보
        name_label = ctk.CTkLabel(
            profile_card,
            text=f"💝 {self.profile_data['name']}님",
            font=("Pretendard", 18),
            text_color=self.colors["white"]
        )
        name_label.pack(pady=5)
        
        # 프로필 정보
        info_frame = ctk.CTkFrame(
            profile_card,
            fg_color="transparent"
        )
        info_frame.pack(pady=15)
        
        # 인스타그램 정보 (클릭 가능)
        insta_frame = ctk.CTkFrame(
            info_frame,
            fg_color="#FFFFFF",
            corner_radius=10
        )
        insta_frame.pack(pady=5, padx=20, fill="x")
        
        insta_label = ctk.CTkLabel(
            insta_frame,
            text=f"📷 @{self.profile_data['instagram']}",
            font=("Pretendard", 14),
            text_color="#0095F6",  # 인스타그램 색상
            cursor="hand2"  # 손가락 커서
        )
        insta_label.pack(pady=8, padx=15)
        # 클릭 이벤트 바인딩
        insta_label.bind("<Button-1>", lambda e: open_instagram_profile(self.profile_data['instagram']))
        
        # MBTI 정보
        mbti_frame = ctk.CTkFrame(
            info_frame,
            fg_color="#FFFFFF",
            corner_radius=10
        )
        mbti_frame.pack(pady=5, padx=20, fill="x")
        
        mbti_label = ctk.CTkLabel(
            mbti_frame,
            text=f"🎭 MBTI: {self.profile_data['mbti']}",
            font=("Pretendard", 14),
            text_color="#4A4A4A"
        )
        mbti_label.pack(pady=8, padx=15)
        
        # 버튼 섹션
        button_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        button_frame.pack(pady=30)
        
        # 친구 찾기 버튼
        find_friend_button = ctk.CTkButton(
            button_frame,
            text="💝 친구 찾기",
            font=("Pretendard", 16, "bold"),
            fg_color="#FF9AAC",
            hover_color="#FF9AAC",
            text_color="#FFFFFF",
            corner_radius=30,
            width=200,
            height=50,
            command=self.start_matching_from_428
        )
        find_friend_button.pack(pady=10)
        
        # 친구목록 버튼
        friend_list_button = ctk.CTkButton(
            button_frame,
            text="👥 친구목록",
            font=("Pretendard", 16, "bold"),
            fg_color="#FF9AAC",
            hover_color="#FF9AAC",
            text_color="#FFFFFF",
            corner_radius=30,
            width=200,
            height=50,
            command=self.show_friend_list
        )
        friend_list_button.pack(pady=10)
        
        # 알림 버튼 프레임 (알림 카운터를 포함하기 위함)
        notification_frame = ctk.CTkFrame(
            button_frame,
            fg_color="transparent"
        )
        notification_frame.pack(pady=10)
        
        # 알림 버튼
        notification_button = ctk.CTkButton(
            notification_frame,
            text="💌 나에게 온 알림",
            font=("Pretendard", 16),
            fg_color="#FF9AAC",
            text_color="#FFFFFF",
            hover_color="#FF9AAC",
            corner_radius=30,
            width=200,
            height=50,
            command=self.show_notifications
        )
        notification_button.pack(side="left")
        
        # 읽지 않은 알림 수 확인
        unread_count = len(self.firebase_manager.get_unread_notifications(self.profile_data['user_id']))
        
        if unread_count > 0:
            # 알림 표시 빨간 사각형
            notification_dot = ctk.CTkLabel(
                notification_frame,
                text="",  # 텍스트 없음
                fg_color="#FF0000",  # 빨간색 배경
                width=10,  # 정사각형 크기
                height=10,
                corner_radius=0  # 모서리를 각지게 (정사각형)
            )
            notification_dot.place(relx=0.85, rely=0.2)  # 버튼 우측 상단에 배치
        
        # 하단 정보
        footer_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        footer_frame.pack(side="bottom", pady=20)
        
        version_label = ctk.CTkLabel(
            footer_frame,
            text="Version 1.0.0 | Made with 💖",
            font=("Pretendard", 12),
            text_color=self.colors["primary"]
        )
        version_label.pack(side="left", padx=10)
        
        # 로그아웃 버튼
        logout_button = ctk.CTkButton(
            footer_frame,
            text="🏠 로그아웃",
            font=("Pretendard", 12),
            fg_color=self.colors["button"],
            hover_color=self.colors["button_hover"],
            text_color=self.colors["white"],
            width=80,
            height=25,
            corner_radius=12,
            command=self.logout
        )
        logout_button.pack(side="right", padx=10)

        # 도움말 아이콘 버튼
        help_button = ctk.CTkButton(
            main_frame,
            text="?",
            font=("Pretendard", 14, "bold"),
            fg_color="#E0E0E0",  # 밝은 회색
            hover_color="#D0D0D0",  # 호버 시 약간 더 어두운 회색
            text_color="#4A4A4A",  # 어두운 회색 텍스트
            width=30,
            height=30,
            corner_radius=15,  # 동그랗게
            command=self.show_user_manual
        )
        help_button.place(relx=0.95, rely=0.95, anchor="se")  # 우측 하단에 배치

    def logout(self):
        """로그아웃 처리"""
        try:
            # 현재 세션 정리
            self.profile_data = None
            
            # 시작 화면으로 이동
            self.show_initial_screen()
            
            messagebox.showinfo("알림", "로그아웃되었습니다.")
            
        except Exception as e:
            print(f"로그아웃 처리 중 오류 발생: {str(e)}")
            messagebox.showerror("오류", "로그아웃 처리 중 오류가 발생했습니다.")

    def show_notifications(self):
        """알림 창 표시"""
        try:
            print("알림창 생성 시작...")  # 디버깅 로그
            
            # 프로필 데이터 확인
            if not hasattr(self, 'profile_data'):
                print("프로필 데이터 속성이 없음")  # 디버깅 로그
                raise Exception("프로필 정보를 찾을 수 없습니다.")
                
            if not self.profile_data:
                print("프로필 데이터가 비어있음")  # 디버깅 로그
                raise Exception("프로필 정보가 비어있습니다.")
                
            if not self.profile_data.get('user_id'):
                print("사용자 ID가 없음")  # 디버깅 로그
                raise Exception("사용자 ID를 찾을 수 없습니다.")
                
            print(f"프로필 데이터 확인 완료: {self.profile_data}")  # 디버깅 로그

            # 알림 창 생성
            notification_window = ctk.CTkToplevel(self.root)
            notification_window.title("💌 나에게 온 알림")
            notification_window.geometry("600x800")
            notification_window.transient(self.root)
            notification_window.grab_set()
            
            print("알림창 기본 설정 완료")  # 디버깅 로그
            
            # 메인 프레임
            main_frame = ctk.CTkScrollableFrame(
                notification_window,
                fg_color=self.colors['background']
            )
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # 제목
            title_label = ctk.CTkLabel(
                main_frame,
                text="💌 나에게 온 알림",
                font=("Pretendard", 24, "bold"),
                text_color=self.colors["dark_gray"]
            )
            title_label.pack(pady=20)
            
            try:
                # 모든 알림 조회
                notifications = self.firebase_manager.get_all_notifications(self.profile_data['user_id'])
                
                if not notifications:
                    # 알림이 없는 경우
                    no_notifications_label = ctk.CTkLabel(
                        main_frame,
                        text="아직 도착한 알림이 없습니다 💌",
                        font=("Pretendard", 16),
                        text_color=self.colors["primary"]
                    )
                    no_notifications_label.pack(pady=30)
                else:
                    # 알림을 최신순으로 정렬
                    notifications.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                    
                    # 읽지 않은 알림 처리를 위한 변수
                    has_unread = False
                    
                    # 알림 목록 표시
                    for notification in notifications:
                        try:
                            # 알림 카드 생성
                            card_frame = ctk.CTkFrame(
                                main_frame,
                                fg_color=self.colors["white"],
                                corner_radius=15
                            )
                            card_frame.pack(fill="x", padx=10, pady=5)
                            
                            # 알림 타입에 따른 아이콘 설정
                            icon = "💝" if notification.get('type') == 'friend_request' else "✨"
                            
                            # 알림 메시지
                            message = notification.get('message', '알 수 없는 알림')
                            message_label = ctk.CTkLabel(
                                card_frame,
                                text=f"{icon} {message}",
                                font=("Pretendard", 14),
                                text_color=self.colors["dark_gray"],
                                wraplength=500
                            )
                            message_label.pack(pady=(15, 10), padx=15)
                            
                            # 친구 요청인 경우 버튼 추가
                            if notification.get('type') == 'friend_request' and notification.get('status') == 'pending':
                                button_frame = ctk.CTkFrame(
                                    card_frame,
                                    fg_color="transparent"
                                )
                                button_frame.pack(pady=(0, 10))
                                
                                # 수락 버튼
                                accept_button = ctk.CTkButton(
                                    button_frame,
                                    text="수락하기",
                                    font=("Pretendard", 12),
                                    fg_color=self.colors["button"],
                                    hover_color=self.colors["button_hover"],
                                    text_color=self.colors["white"],
                                    width=100,
                                    height=30,
                                    command=lambda n=notification: self.handle_friend_request(n, 'accepted', notification_window)
                                )
                                accept_button.pack(side="left", padx=5)
                                
                                # 거절 버튼
                                reject_button = ctk.CTkButton(
                                    button_frame,
                                    text="거절하기",
                                    font=("Pretendard", 12),
                                    fg_color=self.colors["gray"],
                                    hover_color=self.colors["dark_gray"],
                                    text_color=self.colors["white"],
                                    width=100,
                                    height=30,
                                    command=lambda n=notification: self.handle_friend_request(n, 'rejected', notification_window)
                                )
                                reject_button.pack(side="left", padx=5)
                            
                            # 알림 시간 표시
                            if 'created_at' in notification:
                                time_label = ctk.CTkLabel(
                                    card_frame,
                                    text=notification['created_at'],
                                    font=("Pretendard", 10),
                                    text_color=self.colors["gray"]
                                )
                                time_label.pack(pady=(0, 10), padx=15)
                            
                            # 알림을 읽음 상태로 변경
                            if not notification.get('is_read', True):
                                has_unread = True
                                notification_id = notification.get('notification_id')
                                if notification_id:
                                    self.firebase_manager.mark_notification_as_read(notification_id)
                                
                        except Exception as e:
                            print(f"개별 알림 처리 중 오류 발생: {str(e)}")
                            continue
                    
                    # 읽지 않은 알림이 있었다면 홈 화면 새로고침
                    if has_unread:
                        self.show_home_screen()
                
                # 알림 창이 닫힐 때 홈 화면 새로고침
                def on_closing():
                    notification_window.destroy()
                    self.show_home_screen()
                    
                notification_window.protocol("WM_DELETE_WINDOW", on_closing)
                
            except Exception as e:
                print(f"알림 데이터 처리 중 오류 발생: {str(e)}")
                traceback.print_exc()
                messagebox.showerror("오류", "알림 데이터를 처리하는 중 오류가 발생했습니다.")
                notification_window.destroy()
                
        except Exception as e:
            print(f"알림 창 생성 중 오류 발생: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("오류", "알림 창을 생성하는 중 오류가 발생했습니다.")

    def handle_friend_request(self, notification, response, window):
        """친구 요청 처리"""
        try:
            print(f"친구 요청 처리 시작 - 응답: {response}")  # 디버깅 로그
            
            # 요청 상태 업데이트
            if self.firebase_manager.update_friend_request_status(notification['notification_id'], response):
                if response == 'accepted':
                    print("친구 요청 수락됨 - 친구 정보 조회 시작")  # 디버깅 로그
                    
                    # 친구 요청 수락 처리
                    friend_data = self.firebase_manager.get_user_by_id(notification['sender_id'])
                    print(f"조회된 친구 정보: {friend_data}")  # 디버깅 로그
                    
                    if friend_data:
                        messagebox.showinfo(
                            "친구 등록 완료!",
                            f"🎉 {notification.get('sender_nickname', '')}님과 친구가 되었습니다!\n친구 목록을 확인해주세요!"
                        )
                        
                        print("친구 목록 창 갱신 시도")  # 디버깅 로그
                        # 기존에 열려있는 친구 목록 창 찾기
                        friend_list_window = None
                        for widget in self.root.winfo_children():
                            if isinstance(widget, ctk.CTkToplevel):
                                title = widget.title()
                                print(f"발견된 창 제목: {title}")  # 디버깅 로그
                                if title == "친구 목록":
                                    friend_list_window = widget
                                    break
                        
                        # 친구 목록 창이 열려있으면 새로고침
                        if friend_list_window:
                            print("기존 친구 목록 창 새로고침")  # 디버깅 로그
                            friend_list_window.destroy()
                            self.show_friends_list()
                else:
                    messagebox.showinfo("알림", "친구 요청을 거절했습니다.")
                
                print("알림 창 새로고침")  # 디버깅 로그
                # 알림 창 새로고침
                window.destroy()
                self.show_notifications()
                
                # 홈 화면의 알림 카운터 업데이트
                self.update_notification_counter()
                
        except Exception as e:
            print(f"친구 요청 처리 중 오류 발생: {str(e)}")
            traceback.print_exc()  # 상세 오류 정보 출력
            messagebox.showerror("오류", "친구 요청을 처리하는 중 오류가 발생했습니다.")

    def start_matching_from_428(self):
        """428줄부터 매칭 로직 실행"""
        try:
            print("매칭 시작...")  # 디버깅 로그
            
            # 프로필 데이터가 없는 경우 체크
            if not hasattr(self, 'profile_data') or not self.profile_data:
                print("프로필 데이터 없음:", getattr(self, 'profile_data', None))  # 디버깅 로그
                messagebox.showerror("오류", "프로필 정보가 없습니다. 프로필을 먼저 생성해주세요.")
                return
                
            print("현재 프로필 데이터:", self.profile_data)  # 디버깅 로그
                
            # 새 창 생성
            matching_window = ctk.CTkToplevel()
            matching_window.title("💕 능주고등학교 선후배 매칭 💕")
            matching_window.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
            matching_window.configure(fg_color=self.colors["matching_bg"])  # 매칭 화면만 연한 분홍색 배경
            
            # 모달 창으로 설정
            matching_window.transient(self.root)  # 부모 창 설정
            matching_window.grab_set()  # 모달 모드 설정
            
            # 로딩 메시지
            loading_label = ctk.CTkLabel(
                matching_window,
                text="✨ 매칭 시스템 준비중... ✨",
                font=("Pretendard", 20, "bold"),
                text_color="#FF6B6B"
            )
            loading_label.pack(pady=50)
            matching_window.update()
            
            try:
                # 현재 프로필 정보 설정
                student_data = {
                    'user_id': self.profile_data.get('user_id'),  # 실제 user_id 사용
                    'instagram': self.profile_data.get('instagram', ''),
                    'name': self.profile_data.get('name', ''),
                    'nickname': self.profile_data.get('nickname', ''),
                    'grade': int(self.profile_data.get('grade', '1').replace('학년', '')),
                    'gender': self.profile_data.get('gender', ''),
                    'mbti': self.profile_data.get('mbti', ''),
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                print("매칭에 사용될 학생 데이터:", student_data)  # 디버깅 로그
                
                # 오늘의 매칭 시도 횟수 확인
                today = datetime.now().strftime("%Y-%m-%d")
                matching_attempts = self.firebase_manager.get_matching_attempts(student_data['user_id'], today)
                
                if matching_attempts >= 5:
                    messagebox.showwarning(
                        "매칭 제한",
                        "오늘의 매칭 횟수를 모두 사용했습니다.\n내일 다시 시도해주세요!"
                    )
                    matching_window.destroy()
                    return
                
                # StudentMatchingApp 인스턴스 생성
                app = StudentMatchingApp(matching_window)
                app.matching_attempts = matching_attempts  # 매칭 시도 횟수 설정
                
                # 앱 초기화
                app.initialize(student_data)
                
                # 로딩 라벨 제거
                loading_label.destroy()
                
            except Exception as e:
                print("데이터 변환 중 오류:", str(e))  # 디버깅 로그
                raise
            
        except Exception as e:
            print("매칭 시스템 오류:", str(e))  # 디버깅 로그
            print("오류 발생 위치:", e.__traceback__.tb_lineno)  # 오류 발생 라인 번호
            messagebox.showerror("오류", f"매칭 시스템 실행 중 오류가 발생했습니다:\n{str(e)}")
            if 'matching_window' in locals():
                matching_window.destroy()

    def show_privacy_consent(self):
        """개인정보 동의 화면 표시"""
        # 개인정보 동의 팝업
        consent_window = ctk.CTkToplevel(self.root)
        consent_window.title("개인정보 이용 동의")
        consent_window.geometry("600x700")
        consent_window.configure(fg_color=self.colors['background'])
        
        consent_window.transient(self.root)  # 메인 창의 자식 창으로 설정
        consent_window.grab_set()  # 모달 창으로 설정
        
        # 메인 프레임
        main_frame = ctk.CTkFrame(
            consent_window,
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        # 타이틀
        title = ctk.CTkLabel(
            main_frame,
            text="개인정보 이용 동의",
            font=("Pretendard", 32, "bold"),
            text_color=self.colors['title']
        )
        title.pack(pady=(0, 40))
        
        # 동의 내용 프레임
        content_frame = ctk.CTkFrame(
            main_frame, 
            fg_color=self.colors['white'],
            corner_radius=15
        )
        content_frame.pack(fill="both", expand=True, pady=(0, 40))
        
        # 개인정보 동의 텍스트
        consent_text = """
< 능친 만들기 >

귀하의 소중한 개인정보를 수집, 이용, 활용하고자
개인정보보호법에 따라 동의를 얻고 있습니다.

본인의 개인정보를 제공하는 것에 대해
동의해주시겠습니까?

개인정보는 친구 매칭을 위한 목적 외에는
사용되지 않음을 알려드리며,

개인정보 수집에 비동의할 시
프로그램 이용이 어려울 수 있습니다."""
        
        # 이용약관 텍스트 레이블
        text_label = ctk.CTkLabel(
            content_frame,
            text=consent_text,
            font=("Pretendard", 20),
            text_color=self.colors['dark_gray'],  # 검은색으로 변경
            justify="center",
            wraplength=450
        )
        text_label.pack(pady=50, padx=30)
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        button_frame.pack(pady=(0, 30))
        
        # 동의 버튼
        agree_button = ctk.CTkButton(
            button_frame,
            text="동의",
            font=("Pretendard", 20),
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            text_color=self.colors['white'],
            width=200,
            height=50,
            corner_radius=25,
            command=lambda: [consent_window.destroy(), self.show_profile_input()]
        )
        agree_button.pack(side='left', padx=10)
        
        # 비동의 버튼
        disagree_button = ctk.CTkButton(
            button_frame,
            text="비동의",
            font=("Pretendard", 20),
            fg_color='transparent',
            hover_color=self.colors['button_hover'],
            text_color=self.colors['dark_gray'],  # 회색으로 변경
            border_color=self.colors['button'],
            border_width=2,
            width=200,
            height=50,
            corner_radius=25,
            command=lambda: [
                messagebox.showwarning(
                    "알림",
                    "서비스 이용이 불가합니다.",
                    font=("Pretendard", 20)
                ),
                consent_window.destroy()
            ]
        )
        disagree_button.pack(side='left', padx=10)

    def show_profile_input(self):
        """프로필 입력 화면 표시"""
        # 기존 위젯들 제거
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 프로필 입력 프레임
        profile_frame = ctk.CTkFrame(self.root, fg_color=self.colors['background'])
        profile_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 제목
        title_label = ctk.CTkLabel(
            profile_frame,
            text="프로필 입력",
            font=("Pretendard", 24, "bold")
        )
        title_label.pack(pady=20)
        
        # 성별 선택 제목
        gender_title = ctk.CTkLabel(
            profile_frame,
            text="성별 선택",
            font=("Pretendard", 18, "bold"),
            text_color=self.colors['dark_gray']  # 검은색으로 변경
        )
        gender_title.pack(pady=(20, 5))
        
        # 성별 선택 프레임
        gender_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        gender_frame.pack(pady=(20, 10))  # 상단 여백 증가
        
        self.gender_var = tk.StringVar()
        male_btn = ctk.CTkRadioButton(
            gender_frame,
            text="남자",
            variable=self.gender_var,
            value="남자",
            font=("Pretendard", 12)
        )
        male_btn.pack(side="left", padx=10)
        
        female_btn = ctk.CTkRadioButton(
            gender_frame,
            text="여자",
            variable=self.gender_var,
            value="여자",
            font=("Pretendard", 12)
        )
        female_btn.pack(side="left", padx=10)

        # 학년 선택 제목
        grade_title = ctk.CTkLabel(
            profile_frame,
            text="학년 선택",
            font=("Pretendard", 18, "bold"),
            text_color=self.colors['dark_gray']  # 검은색으로 변경
        )
        grade_title.pack(pady=(20, 5))
        
        # 학년 선택
        grade_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        grade_frame.pack(pady=10)
        
        self.grade_var = tk.StringVar()
        grades = ["1학년", "2학년", "3학년"]
        for grade in grades:
            grade_btn = ctk.CTkRadioButton(
                grade_frame,
                text=grade,
                variable=self.grade_var,
                value=grade,
                font=("Pretendard", 12)
            )
            grade_btn.pack(side="left", padx=10)

        # 이름 입력
        name_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        name_frame.pack(pady=10)
        
        # 이름 입력 라벨
        name_label = ctk.CTkLabel(
            name_frame,
            text="이름을 입력해주세요",
            font=("Pretendard", 14),
            text_color=self.colors["white"]
        )
        name_label.pack()
        
        self.name_entry = ctk.CTkEntry(
            name_frame,
            width=200,
            font=("Pretendard", 12),
            placeholder_text="본인 이름 입력"
        )
        self.name_entry.pack(pady=5)
        
        # 별명 입력
        nickname_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        nickname_frame.pack(pady=10)
        
        # 별명 입력 라벨
        nickname_label = ctk.CTkLabel(
            nickname_frame,
            text="별명을 입력해주세요",
            font=("Pretendard", 14),
            text_color=self.colors["white"]
        )
        nickname_label.pack()
        
        # 별명 입력 및 중복확인 버튼을 위한 하위 프레임
        nickname_input_frame = ctk.CTkFrame(nickname_frame, fg_color="transparent")
        nickname_input_frame.pack(pady=5)
        
        self.nickname_entry = ctk.CTkEntry(
            nickname_input_frame,
            width=200,
            font=("Pretendard", 12),
            placeholder_text="별명 입력"
        )
        self.nickname_entry.pack(side="left", padx=(0, 10))
        
        # 중복확인 버튼
        self.check_nickname_button = ctk.CTkButton(
            nickname_input_frame,
            text="중복확인",
            font=("Pretendard", 12),
            width=80,
            fg_color=self.colors['button'],
            hover_color=self.colors['button'],
            text_color=self.colors['white'],  # 하얀색으로 변경
            command=self.check_nickname_duplicate
        )
        self.check_nickname_button.pack(side="left")
        
        # 중복확인 완료 여부
        self.nickname_checked = False
        
        # 별명 입력 필드 변경 감지
        def on_nickname_change(event=None):
            if self.nickname_checked:
                self.nickname_checked = False
                self.check_nickname_button.configure(
                    text="중복확인",
                    fg_color=self.colors['button']  # 파란색에서 핑크색으로 변경
                )
        
        self.nickname_entry.bind('<KeyRelease>', on_nickname_change)
        
        # 인스타그램 아이디 입력
        insta_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        insta_frame.pack(pady=10)
        
        # 인스타그램 아이디 라벨
        insta_label = ctk.CTkLabel(
            insta_frame,
            text="인스타그램 아이디를 입력해주세요",
            font=("Pretendard", 14),
            text_color=self.colors["white"]
        )
        insta_label.pack()
        
        # 인스타그램 아이디 입력 필드
        self.insta_entry = ctk.CTkEntry(
            insta_frame,
            width=200,
            font=("Pretendard", 12)
        )
        self.insta_entry.pack(pady=5)
        self.insta_entry.insert(0, '@')  # 초기값으로 @ 설정
        
        # 인스타그램 아이디 안내 문구
        insta_guide = ctk.CTkLabel(
            insta_frame,
            text="✨ 인스타그램 아이디를 입력해주세요",
            font=("Pretendard", 12),
            text_color=self.colors['subtitle']  # 연한 핑크색
        )
        insta_guide.pack(pady=(0, 10))
        
        # 입력 내용이 변경될 때마다 호출되는 함수
        def on_insta_change(event=None):
            current_text = self.insta_entry.get()
            cursor_position = self.insta_entry.index(tk.INSERT)
            
            if not current_text.startswith('@'):
                self.insta_entry.delete(0, tk.END)
                self.insta_entry.insert(0, '@' + current_text.replace('@', ''))
                self.insta_entry.icursor(cursor_position + 1)
            
            if current_text == '@':
                self.insta_entry.icursor(1)
                
        self.insta_entry.bind('<KeyRelease>', on_insta_change)
        
        # 백스페이스로 @ 삭제 방지
        def prevent_at_deletion(event):
            if event.keysym == 'BackSpace' and self.insta_entry.index(tk.INSERT) <= 1:
                return 'break'
            
        self.insta_entry.bind('<Key>', prevent_at_deletion)
        
        # 다음 버튼
        next_button = ctk.CTkButton(
            profile_frame,
            text="다음",
            font=("Pretendard", 14),
            fg_color=self.colors['button'],
            hover_color=self.colors['button'],
            text_color=self.colors['white'],  # 하얀색으로 변경
            command=self.validate_profile
        )
        next_button.pack(pady=20)
        
    def validate_profile(self):
        """프로필 정보 유효성 검사 및 저장"""
        # 성별 선택 확인
        if not self.gender_var.get():
            messagebox.showerror("오류", "성별을 선택해주세요.")
            return
            
        # 학년 선택 확인
        if not self.grade_var.get():
            messagebox.showerror("오류", "학년을 선택해주세요.")
            return
            
        # 별명 입력 확인
        nickname = self.nickname_entry.get().strip()
        if not nickname:
            messagebox.showerror("오류", "별명을 입력해주세요.")
            return
            
        # 별명 중복 확인 여부 체크
        if not self.nickname_checked:
            messagebox.showerror("오류", "별명 중복 확인을 해주세요.")
            return
            
        # 인스타그램 아이디 확인
        instagram_id = self.insta_entry.get().strip()
        if not instagram_id or instagram_id == '@':
            messagebox.showerror("오류", "인스타그램 아이디를 입력해주세요.")
            return
            
        # 이름 확인
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("오류", "이름을 입력해주세요.")
            return

        # 이름과 인스타그램 아이디 동시 중복 확인
        try:
            users = self.firebase_manager.get_all_users()
            instagram_id_clean = instagram_id.replace('@', '').lower()
            name_clean = name.lower()

            for user in users:
                user_instagram = user.get('instagram', '').lower()
                user_name = user.get('name', '').lower()
                
                if user_instagram == instagram_id_clean and user_name == name_clean:
                    messagebox.showerror(
                        "오류",
                        "이미 존재하는 프로필입니다.\n기존 프로필로 로그인해주세요."
                    )
                    return

        except Exception as e:
            print(f"프로필 중복 확인 중 오류 발생: {str(e)}")
            messagebox.showerror("오류", "프로필 확인 중 오류가 발생했습니다.")
            return
            
        # 임시로 프로필 정보 저장
        self.temp_profile = {
            'gender': self.gender_var.get(),
            'grade': self.grade_var.get(),
            'nickname': nickname,
            'instagram': instagram_id,
            'name': name
        }
        
        # MBTI 테스트 시작
        self.show_mbti_test()

    def check_nickname_duplicate(self):
        """별명 중복 확인"""
        nickname = self.nickname_entry.get().strip()
        if not nickname:
            messagebox.showerror("오류", "별명을 입력해주세요.")
            return

        firebase_manager = FirebaseManager()
        if firebase_manager.check_nickname_exists(nickname):
            messagebox.showerror(
                "오류", 
                "이미 사용 중인 별명입니다.\n다른 별명을 입력해주세요."
            )
            self.nickname_entry.delete(0, tk.END)
            self.nickname_entry.focus()
            self.nickname_checked = False
        else:
            messagebox.showinfo("확인", "사용 가능한 별명입니다!")
            self.nickname_checked = True
            self.check_nickname_button.configure(
                text="✓",
                fg_color=["#2ecc71", "#27ae60"]  # 초록색 계열
            )

    def show_mbti_test(self):
        """MBTI 테스트 창 생성"""
        # MBTI 테스트 창 생성
        test_window = ctk.CTkToplevel(self.root)
        test_window.title("MBTI 성격유형 테스트")
        test_window.geometry("800x800")  # 창 크기 증가
        test_window.transient(self.root)  # 메인 창의 자식 창으로 설정
        test_window.grab_set()  # 모달 창으로 설정
        
        # MBTI 테스트 인스턴스 생성
        self.mbti_test = MBTITest(test_window, self.on_mbti_result)
        
    def on_mbti_result(self, mbti_result):
        """MBTI 테스트 결과 처리"""
        try:
            # 프로필 정보에 MBTI 결과 추가
            self.temp_profile['mbti'] = mbti_result
            
            # Firebase에 저장할 데이터 준비
            profile_data = {
                'gender': self.temp_profile['gender'],
                'grade': self.temp_profile['grade'].replace('학년', ''),  # '1학년' -> '1'
                'nickname': self.temp_profile['nickname'],
                'instagram': self.temp_profile['instagram'].replace('@', ''),  # @ 제거
                'mbti': self.temp_profile['mbti'],
                'name': self.temp_profile['name'],
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print("Firebase에 저장할 프로필 데이터:", profile_data)  # 디버깅 로그
            
            # Firebase에 프로필 저장
            try:
                user_id = self.firebase_manager.save_profile(profile_data)
                if user_id:
                    print(f"Firebase에 프로필 저장 성공 (ID: {user_id})")  # 디버깅 로그
                    
                    # 프로필 데이터 설정
                    self.profile_data = {
                        'user_id': user_id,
                        'nickname': profile_data['nickname'],
                        'instagram': profile_data['instagram'],
                        'grade': profile_data['grade'],
                        'gender': profile_data['gender'],
                        'mbti': profile_data['mbti'],
                        'name': profile_data['name']
                    }
                    
                    messagebox.showinfo("성공", "프로필이 저장되었습니다!")
                    self.show_home_screen()
                else:
                    raise Exception("Firebase 저장 실패: user_id가 반환되지 않음")
            except Exception as e:
                print(f"Firebase 저장 오류: {str(e)}")  # 디버깅 로그
                raise Exception(f"Firebase 저장 실패: {str(e)}")
        except Exception as e:
            error_msg = f"프로필 저장 중 오류가 발생했습니다: {str(e)}"
            print(error_msg)  # 디버깅 로그
            messagebox.showerror("오류", error_msg)
            print("Error details:", e)  # 디버깅 로그

    def run(self):
        self.root.mainloop()

    def show_friend_list(self):
        """친구목록 창 표시"""
        try:
            # 친구목록 창 생성
            friend_list_window = ctk.CTkToplevel(self.root)
            friend_list_window.title("👥 내 친구목록")
            friend_list_window.geometry("600x800")
            friend_list_window.transient(self.root)
            friend_list_window.grab_set()
            
            # 메인 프레임
            main_frame = ctk.CTkScrollableFrame(
                friend_list_window,
                fg_color=self.colors['background']
            )
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # 제목
            title_label = ctk.CTkLabel(
                main_frame,
                text="👥 내 친구목록",
                font=("Pretendard", 24, "bold"),
                text_color=self.colors["dark_gray"]
            )
            title_label.pack(pady=20)
            
            try:
                # Firebase에서 친구 목록 가져오기
                friends = self.firebase_manager.get_friends(self.profile_data['user_id'])
                
                if not friends:
                    # 친구가 없는 경우
                    no_friends_label = ctk.CTkLabel(
                        main_frame,
                        text="아직 친구가 없습니다.\n새로운 친구를 찾아보세요!",
                        font=("Pretendard", 16),
                        text_color=self.colors["gray"]
                    )
                    no_friends_label.pack(pady=50)
                else:
                    # 친구 목록 표시
                    for friend in friends:
                        # 친구 카드 프레임
                        card_frame = ctk.CTkFrame(
                            main_frame,
                            fg_color=self.colors["white"],
                            corner_radius=15
                        )
                        card_frame.pack(fill="x", padx=10, pady=10)
                        
                        # 친구 별명
                        nickname_label = ctk.CTkLabel(
                            card_frame,
                            text=friend['nickname'],
                            font=("Pretendard", 18, "bold"),
                            text_color=self.colors["dark_gray"]
                        )
                        nickname_label.pack(pady=(15, 5))
                        
                        # 프로필 보기 버튼
                        profile_button = ctk.CTkButton(
                            card_frame,
                            text="프로필 보기",
                            font=("Pretendard", 14),
                            fg_color=self.colors["button"],
                            hover_color=self.colors["button_hover"],
                            text_color=self.colors["white"],
                            width=120,
                            height=30,
                            corner_radius=15,
                            command=lambda f=friend: self.show_friend_profile(f)
                        )
                        profile_button.pack(pady=(5, 15))
                        
            except Exception as e:
                print(f"친구 목록 로딩 중 오류 발생: {str(e)}")
                messagebox.showerror("오류", "친구 목록을 불러오는 중 오류가 발생했습니다.")
                
        except Exception as e:
            print(f"친구 목록 창 생성 중 오류 발생: {str(e)}")
            messagebox.showerror("오류", "친구 목록 창을 생성하는 중 오류가 발생했습니다.")

    def show_friend_profile(self, friend):
        """친구 프로필 창 표시"""
        try:
            # 프로필 창 생성
            profile_window = ctk.CTkToplevel(self.root)
            profile_window.title(f"👤 {friend['nickname']}님의 프로필")
            profile_window.geometry("400x600")
            profile_window.transient(self.root)
            profile_window.grab_set()
            
            # 메인 프레임
            main_frame = ctk.CTkFrame(
                profile_window,
                fg_color=self.colors['background']
            )
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # 프로필 카드
            profile_card = ctk.CTkFrame(
                main_frame,
                fg_color=self.colors["white"],
                corner_radius=15
            )
            profile_card.pack(fill="both", expand=True, padx=10, pady=10)
            
            # 프로필 정보 표시
            # 별명
            nickname_label = ctk.CTkLabel(
                profile_card,
                text=f"✨ {friend['nickname']}",
                font=("Pretendard", 24, "bold"),
                text_color=self.colors["dark_gray"]
            )
            nickname_label.pack(pady=(30, 20))
            
            # 학년
            grade_label = ctk.CTkLabel(
                profile_card,
                text=f"🎓 {friend['grade']}학년",
                font=("Pretendard", 16),
                text_color=self.colors["gray"]
            )
            grade_label.pack(pady=10)
            
            # 성별
            gender_label = ctk.CTkLabel(
                profile_card,
                text=f"👤 {friend['gender']}",
                font=("Pretendard", 16),
                text_color=self.colors["gray"]
            )
            gender_label.pack(pady=10)
            
            # MBTI
            if 'mbti' in friend and friend['mbti']:
                mbti_label = ctk.CTkLabel(
                    profile_card,
                    text=f"🎭 MBTI: {friend['mbti']}",
                    font=("Pretendard", 16),
                    text_color=self.colors["gray"]
                )
                mbti_label.pack(pady=10)
            
            # 인스타그램 (클릭 가능)
            insta_label = ctk.CTkLabel(
                profile_card,
                text=f"📷 @{friend['instagram']}",
                font=("Pretendard", 16),
                text_color="#0095F6",  # 인스타그램 색상
                cursor="hand2"  # 손가락 커서
            )
            insta_label.pack(pady=10)
            # 클릭 이벤트 바인딩
            insta_label.bind("<Button-1>", lambda e: open_instagram_profile(friend['instagram']))
            
            # 닫기 버튼
            close_button = ctk.CTkButton(
                profile_card,
                text="닫기",
                font=("Pretendard", 14),
                fg_color=self.colors["button"],
                hover_color=self.colors["button_hover"],
                text_color=self.colors["white"],
                width=120,
                height=30,
                corner_radius=15,
                command=profile_window.destroy
            )
            close_button.pack(pady=(30, 20))
            
        except Exception as e:
            print(f"프로필 창 생성 중 오류 발생: {str(e)}")
            messagebox.showerror("오류", "프로필 창을 생성하는 중 오류가 발생했습니다.")

    def show_friends_list(self):
        """친구 목록 창을 표시합니다."""
        friends_window = ctk.CTkToplevel(self.root)
        friends_window.title("친구 목록")
        friends_window.geometry("400x600")
        
        # 스크롤 가능한 프레임 생성
        scroll_frame = ctk.CTkScrollableFrame(friends_window, width=380, height=580)
        scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 친구 목록 가져오기
        friends = self.firebase_manager.get_friend_profiles(self.profile_data['user_id'])
        
        if not friends:
            no_friends_label = ctk.CTkLabel(
                scroll_frame,
                text="아직 친구가 없습니다 😊",
                font=("Pretendard", 14)
            )
            no_friends_label.pack(pady=20)
            return
        
        # 각 친구의 프로필 카드 생성
        for friend in friends:
            # 친구 카드 프레임
            friend_card = ctk.CTkFrame(scroll_frame, corner_radius=10)
            friend_card.pack(pady=10, padx=5, fill="x")
            
            # 프로필 정보 컨테이너
            info_frame = ctk.CTkFrame(friend_card, fg_color="transparent")
            info_frame.pack(pady=10, padx=10, fill="x")
            
            # 닉네임과 인스타 ID
            name_insta_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            name_insta_frame.pack(fill="x")
            
            name_label = ctk.CTkLabel(
                name_insta_frame,
                text=f"🤗 {friend.get('nickname', '알 수 없음')}",
                font=("Pretendard", 16, "bold")
            )
            name_label.pack(side="left")
            
            # 인스타그램 아이디 (클릭 가능)
            insta_label = ctk.CTkLabel(
                name_insta_frame,
                text=f"📸 @{friend.get('instagram_id', 'unknown')}",
                font=("Pretendard", 14),
                text_color="#0095F6",  # 인스타그램 색상
                cursor="hand2"  # 손가락 커서
            )
            insta_label.pack(side="right")
            # 클릭 이벤트 바인딩
            insta_label.bind("<Button-1>", lambda e, id=friend.get('instagram_id', ''): open_instagram_profile(id))
            
            # MBTI, 성별, 학년 정보
            details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            details_frame.pack(fill="x", pady=(5, 0))
            
            mbti_label = ctk.CTkLabel(
                details_frame,
                text=f"✨ MBTI: {friend.get('mbti', '미설정')}",
                font=("Pretendard", 14)
            )
            mbti_label.pack(side="left")
            
            gender_year_label = ctk.CTkLabel(
                details_frame,
                text=f"👤 {friend.get('gender', '미설정')} | 🎓 {friend.get('grade', '미설정')}학년",
                font=("Pretendard", 14)
            )
            gender_year_label.pack(side="right")
            
            # 구분선
            separator = ctk.CTkFrame(friend_card, height=2, fg_color=self.colors["subtitle"])
            separator.pack(fill="x", padx=10, pady=(5, 0))

    def show_user_manual(self):
        """사용설명서 창을 표시합니다."""
        manual_window = ctk.CTkToplevel(self.root)
        manual_window.title("능친 만들기 사용설명서")
        manual_window.geometry("600x800")
        manual_window.transient(self.root)
        manual_window.grab_set()

        # 스크롤 가능한 프레임
        scroll_frame = ctk.CTkScrollableFrame(
            manual_window,
            fg_color=self.colors["white"]
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 제목
        title = ctk.CTkLabel(
            scroll_frame,
            text="능친 만들기 사용설명서",
            font=("Pretendard", 24, "bold"),
            text_color=self.colors["dark_gray"]
        )
        title.pack(pady=(0, 20))

        # 사용설명서 내용
        manual_sections = [
            ("1. 사용 방법", [
                ("1) 로그인", [
                    "• 프로그램을 실행하면 가장 먼저 로그인 화면이 나옵니다.",
                    "• 자신의 계정 정보를 입력하고 로그인하세요.",
                    "• 로그인 후 메인 화면으로 이동합니다."
                ]),
                ("2) 친구 매칭", [
                    "• 메인 화면에서 '친구 매칭 시작' 버튼을 누르면 랜덤으로 친구가 매칭됩니다.",
                    "• 매칭된 친구의 기본 정보가 화면에 표시됩니다."
                ]),
                ("3) 수락 또는 거절", [
                    "• 매칭된 친구에 대해 '수락' 또는 '거절' 버튼을 선택할 수 있습니다.",
                    "• 수락하면 상대방이 수락 여부를 확인할 수 있으며, 거절하면 매칭이 취소됩니다."
                ])
            ]),
            ("2. 알림 및 친구 목록 확인", [
                "• 하단 메뉴 또는 사이드 메뉴에서 '내 알림' 또는 '친구 목록'을 선택하세요.",
                "• 여기에서 상대방이 나를 수락했는지, 내가 수락한 친구 목록은 어떤지 확인할 수 있습니다.",
                "• 아직 수락되지 않은 경우에는 '대기 중' 상태로 표시됩니다."
            ]),
            ("3. 인스타그램 계정 확인", [
                "• 서로 수락이 완료된 친구는 그 친구 인스타 계정으로 들어갈 수 있는 버튼이 생깁니다.",
                "• 버튼을 클릭하면 친구의 인스타그램 프로필 페이지로 이동합니다.",
                "• 상대방의 계정이 비공개인 경우, 팔로우 요청을 따로 해야 할 수 있습니다."
            ]),
            ("4. 주의사항 및 팁", [
                "• 인스타그램 계정은 각 사용자가 직접 등록해야 하며, 정확한 URL을 입력해 주세요.",
                "• 상대방이 수락하지 않은 경우 인스타그램 링크는 표시되지 않습니다.",
                "• 매칭은 랜덤으로 진행되므로, 원하는 친구가 매칭되지 않을 수도 있습니다.",
                "• 알림이 갱신되기까지 약간의 시간이 걸릴 수 있습니다. 잠시 후 다시 확인해 주세요."
            ])
        ]

        # 각 섹션 생성
        for section_title, content in manual_sections:
            # 섹션 제목
            section_label = ctk.CTkLabel(
                scroll_frame,
                text=section_title,
                font=("Pretendard", 18, "bold"),
                text_color=self.colors["dark_gray"]
            )
            section_label.pack(pady=(20, 10), anchor="w")

            # 섹션 내용
            if isinstance(content[0], tuple):  # 하위 섹션이 있는 경우
                for subsection_title, subsection_content in content:
                    # 하위 섹션 제목
                    subsection_label = ctk.CTkLabel(
                        scroll_frame,
                        text=subsection_title,
                        font=("Pretendard", 16, "bold"),
                        text_color=self.colors["dark_gray"]
                    )
                    subsection_label.pack(pady=(10, 5), anchor="w", padx=20)

                    # 하위 섹션 내용
                    for line in subsection_content:
                        content_label = ctk.CTkLabel(
                            scroll_frame,
                            text=line,
                            font=("Pretendard", 14),
                            text_color=self.colors["gray"],
                            wraplength=520,
                            justify="left"
                        )
                        content_label.pack(pady=2, anchor="w", padx=40)
            else:  # 하위 섹션이 없는 경우
                for line in content:
                    content_label = ctk.CTkLabel(
                        scroll_frame,
                        text=line,
                        font=("Pretendard", 14),
                        text_color=self.colors["gray"],
                        wraplength=520,
                        justify="left"
                    )
                    content_label.pack(pady=2, anchor="w", padx=20)

        # 닫기 버튼
        close_button = ctk.CTkButton(
            manual_window,
            text="닫기",
            font=("Pretendard", 14),
            fg_color=self.colors["button"],
            hover_color=self.colors["button_hover"],
            text_color=self.colors["white"],
            width=100,
            height=30,
            corner_radius=15,
            command=manual_window.destroy
        )
        close_button.pack(pady=20)

    def update_notification_counter(self):
        """알림 카운터 업데이트"""
        try:
            if hasattr(self, 'profile_data') and self.profile_data and self.profile_data.get('user_id'):
                unread_count = len(self.firebase_manager.get_unread_notifications(self.profile_data['user_id']))
                # 알림 카운터 업데이트 로직은 show_home_screen에서 처리됨
                self.show_home_screen()
        except Exception as e:
            print(f"알림 카운터 업데이트 중 오류 발생: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    app = FriendFinderApp()
    app.run() 