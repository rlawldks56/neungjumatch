from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'neungchin-secret-key'  # 세션 사용을 위한 키

# MBTI 질문 데이터 (main.py에서 참고)
mbti_questions = [
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

mbti_descriptions = {
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

# 임시 매칭 데이터 (세션에 저장)
def get_matchings():
    return session.get('matchings', [])
def save_matching(matching):
    matchings = session.get('matchings', [])
    matchings.append(matching)
    session['matchings'] = matchings

def get_profile():
    return session.get('profile', {})

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/mbti', methods=['GET', 'POST'])
def mbti():
    if 'mbti_answers' not in session:
        session['mbti_answers'] = []
    answers = session['mbti_answers']
    q_idx = len(answers)
    if request.method == 'POST':
        selected = request.form.get('answer')
        if selected is not None:
            answers.append(selected)
            session['mbti_answers'] = answers
            q_idx += 1
    if q_idx >= len(mbti_questions):
        return redirect(url_for('mbti_result'))
    question = mbti_questions[q_idx]
    return render_template('mbti.html', q_idx=q_idx, total=len(mbti_questions), question=question)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        instagram = request.form.get('instagram')
        name = request.form.get('name')
        mbti = request.form.get('mbti')
        session['profile'] = {
            'nickname': nickname,
            'instagram': instagram,
            'name': name,
            'mbti': mbti
        }
        return redirect(url_for('profile'))
    profile = session.get('profile', {})
    mbti = profile.get('mbti', session.get('last_mbti', ''))
    return render_template('profile.html', profile=profile, mbti=mbti)

# MBTI 검사 결과 저장 (mbti_result에서)
@app.route('/mbti/result')
def mbti_result():
    answers = session.get('mbti_answers', [])
    if len(answers) != len(mbti_questions):
        return redirect(url_for('mbti'))
    mbti_type = ''.join(answers)
    description = mbti_descriptions.get(mbti_type, '알 수 없는 유형')
    session['last_mbti'] = mbti_type  # 최근 MBTI 결과 세션에 저장
    session.pop('mbti_answers', None)
    return render_template('mbti_result.html', mbti=mbti_type, description=description)

@app.route('/matching', methods=['GET', 'POST'])
def matching():
    profile = get_profile()
    if not profile:
        flash('프로필을 먼저 입력해주세요.')
        return redirect(url_for('profile'))
    # 임시로 랜덤 매칭 후보 1명 생성 (실제 구현시 DB에서 필터)
    import random
    candidates = [
        {'nickname': '친구A', 'instagram': 'friendA', 'name': '김친구', 'mbti': 'ENFP'},
        {'nickname': '친구B', 'instagram': 'friendB', 'name': '이친구', 'mbti': 'ISTJ'},
        {'nickname': '친구C', 'instagram': 'friendC', 'name': '박친구', 'mbti': 'INFJ'}
    ]
    candidate = random.choice(candidates)
    if request.method == 'POST':
        # 매칭 요청
        save_matching({'from': profile['nickname'], 'to': candidate['nickname'], 'status': 'pending'})
        flash(f"{candidate['nickname']}님에게 매칭 요청을 보냈습니다!")
        return redirect(url_for('matching'))
    return render_template('matching.html', candidate=candidate)

@app.route('/matching/requests')
def matching_requests():
    matchings = get_matchings()
    return render_template('matching_requests.html', matchings=matchings)

@app.route('/matching/accept/<int:idx>')
def matching_accept(idx):
    matchings = get_matchings()
    if 0 <= idx < len(matchings):
        matchings[idx]['status'] = 'accepted'
        session['matchings'] = matchings
        flash('매칭을 수락했습니다!')
    return redirect(url_for('matching_requests'))

@app.route('/matching/reject/<int:idx>')
def matching_reject(idx):
    matchings = get_matchings()
    if 0 <= idx < len(matchings):
        matchings[idx]['status'] = 'rejected'
        session['matchings'] = matchings
        flash('매칭을 거절했습니다.')
    return redirect(url_for('matching_requests'))

@app.route('/friends')
def friends():
    # 수락된 매칭을 친구 목록으로 변환
    matchings = get_matchings()
    friends = []
    for m in matchings:
        if m['status'] == 'accepted':
            friends.append({
                'nickname': m['to'] if m['from'] == get_profile().get('nickname') else m['from'],
                'name': '친구',  # 임시 데이터
                'instagram': 'friend_insta',
                'mbti': 'ENFP'  # 임시 데이터
            })
    return render_template('friends.html', friends=friends)

@app.route('/friends/profile/<nickname>')
def friend_profile(nickname):
    # 임시 친구 데이터
    friend = {
        'nickname': nickname,
        'name': '친구',
        'instagram': 'friend_insta',
        'mbti': 'ENFP'
    }
    return render_template('friend_profile.html', friend=friend)

@app.route('/notifications')
def notifications():
    # 임시 알림 데이터
    notifications = [
        {'type': 'matching', 'message': '친구A님이 매칭을 요청했습니다.', 'time': '방금 전'},
        {'type': 'friend', 'message': '친구B님이 친구 요청을 보냈습니다.', 'time': '5분 전'}
    ]
    return render_template('notifications.html', notifications=notifications)

if __name__ == '__main__':
    app.run(debug=True) 