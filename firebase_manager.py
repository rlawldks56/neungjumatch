import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CONFIG, COLLECTION_NAME, FIREBASE_TEST_MODE, DATABASE_URL
import uuid
from datetime import datetime
import json
import os
import traceback
import random

class FirebaseManager:
    _instance = None
    TEST_DATA_FILE = "test_data.json"  # 테스트 데이터를 저장할 파일
    _initialized = False
    
    def __new__(cls, test_mode=None):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, test_mode=None):
        if self._initialized:
            return
            
        self.test_mode = test_mode if test_mode is not None else FIREBASE_TEST_MODE
        print(f"Firebase 매니저 초기화 (테스트 모드: {self.test_mode})")
        
        if self.test_mode:
            self.test_data = self.load_test_data()
            print("테스트 데이터 초기화 완료")
            self._initialized = True
            return

        try:
            # Firebase 앱이 이미 초기화되어 있는지 확인
            if not firebase_admin._apps:
                if not os.path.exists(FIREBASE_CONFIG):
                    raise FileNotFoundError(f"Firebase 설정 파일을 찾을 수 없습니다: {FIREBASE_CONFIG}")

                try:
                    cred = credentials.Certificate(FIREBASE_CONFIG)
                    firebase_admin.initialize_app(cred, {
                        'databaseURL': DATABASE_URL
                    })
                    print("Firebase 앱 초기화 성공")
                except ValueError as ve:
                    print(f"Firebase 인증 정보가 올바르지 않습니다: {str(ve)}")
                    raise
                except Exception as e:
                    print(f"Firebase 초기화 중 오류 발생: {str(e)}")
                    raise

            # Firestore 클라이언트 생성
            try:
                self.db = firestore.client()
                print("Firestore 클라이언트 생성 성공")
            except Exception as e:
                print(f"Firestore 클라이언트 생성 실패: {str(e)}")
                raise

        except Exception as e:
            print("Firebase 연결 실패, 테스트 모드로 전환합니다.")
            print(f"오류 내용: {str(e)}")
            traceback.print_exc()
            self.test_mode = True
            self.test_data = self.load_test_data()

        self._initialized = True
        
    def load_test_data(self):
        """테스트 데이터 파일에서 데이터 불러오기"""
        try:
            if os.path.exists(self.TEST_DATA_FILE):
                with open(self.TEST_DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"테스트 데이터 파일 로드 완료: {len(data.get('students', []))}명의 학생 데이터")
                return data
        except Exception as e:
            print(f"테스트 데이터 파일 로드 실패: {str(e)}")
        
        # 파일이 없거나 로드 실패 시 기본 데이터 구조 반환
        return {
            'students': [],
            'matchings': []
        }

    def save_test_data(self):
        """테스트 데이터를 파일에 저장"""
        try:
            with open(self.TEST_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.test_data, f, ensure_ascii=False, indent=2)
            print("테스트 데이터 파일 저장 완료")
            return True
        except Exception as e:
            print(f"테스트 데이터 파일 저장 실패: {str(e)}")
            return False

    def save_profile(self, profile_data):
        """프로필 저장"""
        try:
            if self.test_mode:
                user_id = str(uuid.uuid4())
                profile_data['user_id'] = user_id
                self.test_data['students'].append(profile_data)
                self.save_test_data()
                print(f"테스트 모드: 프로필 저장 완료 (ID: {user_id})")
                return user_id
            else:
                # Firestore에 저장
                print("Firestore에 프로필 저장 시도...")
                print(f"저장할 데이터: {profile_data}")
                
                user_id = str(uuid.uuid4())
                doc_ref = self.db.collection('students').document(user_id)
                profile_data['user_id'] = user_id
                
                print(f"문서 경로: students/{user_id}")
                doc_ref.set(profile_data)
                print(f"Firestore 프로필 저장 완료 (ID: {user_id})")
                return user_id
        except Exception as e:
            print(f"프로필 저장 중 오류 발생: {str(e)}")
            print("오류 상세 정보:")
            traceback.print_exc()
            return None

    def get_all_users(self):
        """모든 사용자 조회"""
        try:
            if self.test_mode:
                return self.test_data['students']
            else:
                users = []
                docs = self.db.collection('students').stream()
                for doc in docs:
                    user_data = doc.to_dict()
                    user_data['user_id'] = doc.id
                    users.append(user_data)
                return users
        except Exception as e:
            print(f"사용자 조회 오류: {str(e)}")
            return []

    def save_matching(self, matching_data):
        """매칭 정보 저장"""
        try:
            if self.test_mode:
                matching_id = str(uuid.uuid4())
                matching_data['matching_id'] = matching_id
                self.test_data['matchings'].append(matching_data)
                self.save_test_data()  # 파일에 저장
                return True
            else:
                # Firestore에 저장
                matching_id = str(uuid.uuid4())
                doc_ref = self.db.collection('matchings').document(matching_id)
                matching_data['matching_id'] = matching_id
                doc_ref.set(matching_data)
                return True
        except Exception as e:
            print(f"매칭 저장 오류: {str(e)}")
            return False

    def get_matchings_for_user(self, user_id):
        """사용자의 매칭 요청 조회"""
        try:
            if self.test_mode:
                return [m for m in self.test_data['matchings'] 
                       if m['sender_id'] == user_id or m['receiver_id'] == user_id]
            else:
                matchings = []
                # 보낸 매칭 요청
                sent = self.db.collection('matchings').where('sender_id', '==', user_id).stream()
                # 받은 매칭 요청
                received = self.db.collection('matchings').where('receiver_id', '==', user_id).stream()
                
                for doc in list(sent) + list(received):
                    matching_data = doc.to_dict()
                    matching_data['id'] = doc.id
                    matchings.append(matching_data)
                return matchings
        except Exception as e:
            print(f"매칭 조회 오류: {str(e)}")
            return []

    def update_matching(self, matching_data):
        """매칭 상태 업데이트"""
        try:
            if self.test_mode:
                for match in self.test_data['matchings']:
                    if match['matching_id'] == matching_data['matching_id']:
                        match.update(matching_data)
                        self.save_test_data()  # 파일에 저장
                        return True
                return False
            else:
                # Firestore 업데이트
                doc_ref = self.db.collection('matchings').document(matching_data['matching_id'])
                doc_ref.update(matching_data)
                return True
        except Exception as e:
            print(f"매칭 업데이트 오류: {str(e)}")
            return False
    
    def get_profile(self, user_id):
        """사용자 프로필 조회"""
        try:
            if self.test_mode:
                for student in self.test_data['students']:
                    if student.get('user_id') == user_id:
                        return student
                return None
            
            doc = self.db.collection(COLLECTION_NAME).document(user_id).get()
            if doc.exists:
                profile_data = doc.to_dict()
                profile_data['user_id'] = doc.id  # user_id 추가
                return profile_data
            return None
        except Exception as e:
            print(f"프로필 조회 중 오류 발생: {str(e)}")
            raise
    
    def update_profile(self, user_id, profile_data):
        """프로필 정보 업데이트"""
        try:
            if self.test_mode:
                for student in self.test_data['students']:
                    if student['id'] == user_id:
                        student.update(profile_data)
                        return True
                return False
            
            profile_data['updated_at'] = firestore.SERVER_TIMESTAMP
            self.db.collection(COLLECTION_NAME).document(user_id).update(profile_data)
            return True
        except Exception as e:
            print(f"프로필 업데이트 중 오류 발생: {str(e)}")
            raise
    
    def delete_profile(self, user_id):
        """프로필 삭제"""
        try:
            if self.test_mode:
                self.test_data['students'] = [s for s in self.test_data['students'] if s['id'] != user_id]
                return True
            
            self.db.collection(COLLECTION_NAME).document(user_id).delete()
            return True
        except Exception as e:
            print(f"프로필 삭제 중 오류 발생: {str(e)}")
            raise
    
    def get_all_profiles(self):
        """모든 프로필 조회"""
        try:
            if self.test_mode:
                return self.test_data['students']
            
            docs = self.db.collection(COLLECTION_NAME).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"프로필 목록 조회 중 오류 발생: {str(e)}")
            raise
            
    def create_matching(self, from_id, to_id):
        """매칭 요청 생성"""
        try:
            # 이미 존재하는 매칭 확인
            existing_matching = self.get_existing_matching(from_id, to_id)
            if existing_matching:
                return existing_matching

            if self.test_mode:
                matching = {
                    'id': str(uuid.uuid4()),
                    'from_id': from_id,
                    'to_id': to_id,
                    'status': 'pending',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                self.test_data['matchings'].append(matching)
                return matching
            
            matching_id = str(uuid.uuid4())
            matching_data = {
                'from_id': from_id,
                'to_id': to_id,
                'status': 'pending',
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            self.db.collection('matchings').document(matching_id).set(matching_data)
            return matching_data
        except Exception as e:
            print(f"매칭 생성 중 오류 발생: {str(e)}")
            raise
            
    def get_matchings(self, user_id):
        """사용자의 매칭 요청 목록 조회"""
        try:
            if self.test_mode:
                return [m for m in self.test_data['matchings'] 
                       if m['to_id'] == user_id or m['from_id'] == user_id]
            
            # 받은 매칭 요청과 보낸 매칭 요청 모두 조회
            received = self.db.collection('matchings').where('to_id', '==', user_id).stream()
            sent = self.db.collection('matchings').where('from_id', '==', user_id).stream()
            
            return [doc.to_dict() for doc in list(received) + list(sent)]
        except Exception as e:
            print(f"매칭 목록 조회 중 오류 발생: {str(e)}")
            raise

    def get_existing_matching(self, from_id, to_id):
        """기존 매칭 요청 확인"""
        try:
            if self.test_mode:
                for matching in self.test_data['matchings']:
                    if (matching['from_id'] == from_id and matching['to_id'] == to_id) or \
                       (matching['from_id'] == to_id and matching['to_id'] == from_id):
                        return matching
                return None
            
            # 양방향 매칭 확인
            matching1 = self.db.collection('matchings').where('from_id', '==', from_id).where('to_id', '==', to_id).limit(1).stream()
            matching2 = self.db.collection('matchings').where('from_id', '==', to_id).where('to_id', '==', from_id).limit(1).stream()
            
            matching1_list = list(matching1)
            matching2_list = list(matching2)
            
            if matching1_list:
                return matching1_list[0].to_dict()
            if matching2_list:
                return matching2_list[0].to_dict()
            return None
        except Exception as e:
            print(f"기존 매칭 확인 중 오류 발생: {str(e)}")
            raise

    def update_matching_status(self, from_id, to_id, status):
        """매칭 상태 업데이트"""
        try:
            if not status in ['pending', 'accepted', 'rejected']:
                raise ValueError("Invalid matching status")

            matching = self.get_existing_matching(from_id, to_id)
            if not matching:
                raise ValueError("Matching not found")

            if self.test_mode:
                for m in self.test_data['matchings']:
                    if (m['from_id'] == from_id and m['to_id'] == to_id) or \
                       (m['from_id'] == to_id and m['to_id'] == from_id):
                        m['status'] = status
                        m['updated_at'] = datetime.now()
                        return m
                return None

            # Firestore에서 매칭 문서 찾기
            matching_query = self.db.collection('matchings').where('from_id', '==', from_id).where('to_id', '==', to_id)
            docs = list(matching_query.stream())
            
            if not docs:
                matching_query = self.db.collection('matchings').where('from_id', '==', to_id).where('to_id', '==', from_id)
                docs = list(matching_query.stream())

            if docs:
                doc_ref = docs[0].reference
                doc_ref.update({
                    'status': status,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
                return doc_ref.get().to_dict()
            return None
        except Exception as e:
            print(f"매칭 상태 업데이트 중 오류 발생: {str(e)}")
            raise

    def check_nickname_exists(self, nickname):
        """별명 중복 체크"""
        try:
            if self.test_mode:
                return any(student.get('nickname') == nickname for student in self.test_data['students'])
            else:
                # Firestore에서 별명으로 검색
                docs = self.db.collection('students').where('nickname', '==', nickname).limit(1).stream()
                return len(list(docs)) > 0
        except Exception as e:
            print(f"별명 중복 체크 중 오류 발생: {str(e)}")
            return False

    def get_matching_attempts(self, user_id, date):
        """특정 날짜의 매칭 시도 횟수 조회"""
        try:
            if self.test_mode:
                return 0
                
            doc = self.db.collection('matching_attempts').document(f"{user_id}_{date}").get()
            if doc.exists:
                return doc.to_dict().get('attempts', 0)
            return 0
        except Exception as e:
            print(f"매칭 시도 횟수 조회 중 오류: {str(e)}")
            return 0
            
    def increment_matching_attempts(self, user_id, date):
        """매칭 시도 횟수 증가"""
        try:
            if self.test_mode:
                return True
                
            doc_ref = self.db.collection('matching_attempts').document(f"{user_id}_{date}")
            doc = doc_ref.get()
            
            if doc.exists:
                current_attempts = doc.to_dict().get('attempts', 0)
                doc_ref.update({
                    'attempts': current_attempts + 1,
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                doc_ref.set({
                    'user_id': user_id,
                    'date': date,
                    'attempts': 1,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            return True
        except Exception as e:
            print(f"매칭 시도 횟수 증가 중 오류: {str(e)}")
            return False

    def reset_matching_attempts(self, user_id, date):
        """매칭 시도 횟수 리셋"""
        try:
            if self.test_mode:
                return True
                
            doc_ref = self.db.collection('matching_attempts').document(f"{user_id}_{date}")
            doc = doc_ref.get()
            
            if doc.exists:
                doc_ref.update({
                    'attempts': 0,
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                doc_ref.set({
                    'user_id': user_id,
                    'date': date,
                    'attempts': 0,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            return True
        except Exception as e:
            print(f"매칭 시도 횟수 리셋 중 오류 발생: {str(e)}")
            return False

    def get_last_reset_date(self, user_id):
        """마지막 리셋 날짜 조회"""
        try:
            if self.test_mode:
                return None
                
            doc = self.db.collection('matching_attempts').document(f"{user_id}_last_reset").get()
            if doc.exists:
                return doc.to_dict().get('last_reset_date', None)
            return None
        except Exception as e:
            print(f"마지막 리셋 날짜 조회 중 오류 발생: {str(e)}")
            return None

    # 알림 관련 새로운 메서드들
    def save_notification(self, notification_data):
        """알림 저장"""
        try:
            doc_ref = self.db.collection('notifications').document()
            notification_data['notification_id'] = doc_ref.id
            notification_data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            notification_data['is_read'] = False
            doc_ref.set(notification_data)
            return doc_ref.id
        except Exception as e:
            print(f"알림 저장 중 오류 발생: {str(e)}")
            return None

    def get_unread_notifications(self, user_id):
        """읽지 않은 알림 조회"""
        try:
            docs = self.db.collection('notifications')\
                .where('receiver_id', '==', user_id)\
                .where('is_read', '==', False)\
                .stream()
            notifications = []
            for doc in docs:
                notification = doc.to_dict()
                notification['notification_id'] = doc.id
                notifications.append(notification)
            return notifications
        except Exception as e:
            print(f"읽지 않은 알림 조회 중 오류 발생: {str(e)}")
            return []

    def get_all_notifications(self, user_id):
        """모든 알림 조회"""
        try:
            docs = self.db.collection('notifications')\
                .where('receiver_id', '==', user_id)\
                .stream()
            notifications = []
            for doc in docs:
                notification = doc.to_dict()
                notification['notification_id'] = doc.id
                notifications.append(notification)
            return notifications
        except Exception as e:
            print(f"알림 조회 중 오류 발생: {str(e)}")
            return []

    def mark_notification_as_read(self, notification_id):
        """알림을 읽음 상태로 변경"""
        try:
            self.db.collection('notifications').document(notification_id).update({
                'is_read': True,
                'read_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return True
        except Exception as e:
            print(f"알림 상태 업데이트 중 오류 발생: {str(e)}")
            return False

    def save_friend_request(self, sender_id, receiver_id, sender_nickname, sender_instagram=None):
        """친구 요청 알림 저장"""
        try:
            # 발신자 정보 조회
            if not sender_instagram:
                sender = next((user for user in self.get_all_users() if user['user_id'] == sender_id), None)
                if sender:
                    sender_instagram = sender.get('instagram', '')

            notification_data = {
                'type': 'friend_request',
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'sender_nickname': sender_nickname,
                'sender_instagram': sender_instagram,
                'message': f"{sender_nickname}님이 친구 요청을 보냈습니다.",
                'status': 'pending'
            }
            return self.save_notification(notification_data)
        except Exception as e:
            print(f"친구 요청 저장 중 오류 발생: {str(e)}")
            return None

    def update_friend_request_status(self, notification_id, status):
        """친구 요청 상태 업데이트"""
        try:
            self.db.collection('notifications').document(notification_id).update({
                'status': status,
                'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return True
        except Exception as e:
            print(f"친구 요청 상태 업데이트 중 오류 발생: {str(e)}")
            return False

    def send_accept_notification(self, sender_id, receiver_id, sender_nickname, instagram_id):
        """친구 요청 수락 알림 저장"""
        try:
            notification_data = {
                'type': 'friend_accept',
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'sender_nickname': sender_nickname,
                'message': f"{sender_nickname}님이 친구 요청을 수락했습니다.",
                'instagram_id': instagram_id
            }
            return self.save_notification(notification_data)
        except Exception as e:
            print(f"수락 알림 저장 중 오류 발생: {str(e)}")
            return None

    def get_friends(self, user_id):
        """사용자의 친구 목록을 가져옵니다."""
        try:
            # 수락된 친구 요청 조회
            accepted_requests = self.db.collection('notifications').where('type', '==', 'friend_request').where('status', '==', 'accepted').get()
            
            friends = []
            for request in accepted_requests:
                request_data = request.to_dict()
                
                # 현재 사용자가 수신자인 경우
                if request_data.get('receiver_id') == user_id:
                    sender = self.get_user_by_id(request_data.get('sender_id'))
                    if sender:
                        friends.append(sender)
                
                # 현재 사용자가 발신자인 경우
                elif request_data.get('sender_id') == user_id:
                    receiver = self.get_user_by_id(request_data.get('receiver_id'))
                    if receiver:
                        friends.append(receiver)
            
            return friends
            
        except Exception as e:
            print(f"친구 목록 조회 중 오류 발생: {str(e)}")
            return []
            
    def get_user_by_id(self, user_id):
        """사용자 ID로 사용자 정보를 가져옵니다."""
        try:
            user_doc = self.db.collection('students').document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                user_data['user_id'] = user_id
                return user_data
            return None
        except Exception as e:
            print(f"사용자 정보 조회 중 오류 발생: {str(e)}")
            return None

    def check_mutual_acceptance(self, user1_id, user2_id):
        """두 사용자 간의 상호 친구 수락 여부를 확인합니다."""
        try:
            # 양방향 친구 요청 확인
            requests = self.db.collection('notifications')\
                .where('type', '==', 'friend_request')\
                .where('status', '==', 'accepted')\
                .stream()
            
            requests = list(requests)
            user1_accepted = False
            user2_accepted = False
            
            for request in requests:
                data = request.to_dict()
                # user1이 보내고 user2가 수락한 경우
                if data.get('sender_id') == user1_id and data.get('receiver_id') == user2_id:
                    user2_accepted = True
                # user2가 보내고 user1이 수락한 경우
                elif data.get('sender_id') == user2_id and data.get('receiver_id') == user1_id:
                    user1_accepted = True
                
                if user1_accepted and user2_accepted:
                    return True
            
            return False
            
        except Exception as e:
            print(f"상호 수락 확인 중 오류 발생: {str(e)}")
            return False

    def get_friend_profiles(self, user_id):
        """사용자의 친구 목록과 각 친구의 전체 프로필 정보를 가져옵니다."""
        try:
            print(f"친구 프로필 조회 시작 - 사용자 ID: {user_id}")  # 디버깅 로그
            
            # 수락된 친구 요청 조회 (보낸 요청)
            sent_requests = self.db.collection('notifications')\
                .where('sender_id', '==', user_id)\
                .where('type', '==', 'friend_request')\
                .where('status', '==', 'accepted')\
                .stream()
            
            # 수락된 친구 요청 조회 (받은 요청)
            received_requests = self.db.collection('notifications')\
                .where('receiver_id', '==', user_id)\
                .where('type', '==', 'friend_request')\
                .where('status', '==', 'accepted')\
                .stream()
            
            friend_profiles = []
            processed_ids = set()  # 중복 방지를 위한 세트
            
            print("수락된 친구 요청 처리 시작")  # 디버깅 로그
            
            # 보낸 요청에서 친구 정보 수집
            for request in sent_requests:
                request_data = request.to_dict()
                friend_id = request_data.get('receiver_id')
                print(f"보낸 요청 처리 - 친구 ID: {friend_id}")  # 디버깅 로그
                
                if friend_id and friend_id not in processed_ids:
                    friend_doc = self.db.collection('students').document(friend_id).get()
                    if friend_doc.exists:
                        friend_data = friend_doc.to_dict()
                        friend_data['user_id'] = friend_id
                        friend_profiles.append(friend_data)
                        processed_ids.add(friend_id)
                        print(f"친구 정보 추가됨: {friend_data.get('nickname')}")  # 디버깅 로그
            
            # 받은 요청에서 친구 정보 수집
            for request in received_requests:
                request_data = request.to_dict()
                friend_id = request_data.get('sender_id')
                print(f"받은 요청 처리 - 친구 ID: {friend_id}")  # 디버깅 로그
                
                if friend_id and friend_id not in processed_ids:
                    friend_doc = self.db.collection('students').document(friend_id).get()
                    if friend_doc.exists:
                        friend_data = friend_doc.to_dict()
                        friend_data['user_id'] = friend_id
                        friend_profiles.append(friend_data)
                        processed_ids.add(friend_id)
                        print(f"친구 정보 추가됨: {friend_data.get('nickname')}")  # 디버깅 로그
            
            print(f"총 {len(friend_profiles)}명의 친구 프로필 조회됨")  # 디버깅 로그
            return friend_profiles
            
        except Exception as e:
            print(f"친구 프로필 조회 중 오류 발생: {str(e)}")
            return [] 

    def get_filtered_users(self, current_id, current_instagram, target_grade=None, compatible_mbti_types=None):
        """필터링된 사용자 목록을 가져옵니다."""
        try:
            if self.test_mode:
                # 테스트 모드에서는 기존 로직 유지
                filtered_users = []
                for student in self.test_data['students']:
                    if self._check_user_eligibility(
                        student, 
                        current_id, 
                        current_instagram, 
                        target_grade, 
                        compatible_mbti_types
                    ):
                        filtered_users.append(student)
                return random.choice(filtered_users) if filtered_users else None
            
            # 기본 쿼리 생성
            query = self.db.collection('students')
            
            # 학년 필터 적용
            if target_grade:
                query = query.where('grade', '==', str(target_grade))
            
            # 최적화를 위해 limit 설정 (최대 50명까지만 가져옴)
            docs = list(query.limit(50).stream())
            eligible_users = []
            
            for doc in docs:
                student = doc.to_dict()
                student['user_id'] = doc.id
                
                if self._check_user_eligibility(
                    student, 
                    current_id, 
                    current_instagram, 
                    target_grade, 
                    compatible_mbti_types
                ):
                    eligible_users.append(student)
            
            # 적합한 사용자 중에서 랜덤 선택
            return random.choice(eligible_users) if eligible_users else None
            
        except Exception as e:
            print(f"필터링된 사용자 조회 중 오류 발생: {str(e)}")
            traceback.print_exc()
            return None

    def _check_user_eligibility(self, student, current_id, current_instagram, target_grade, compatible_mbti_types):
        """사용자가 매칭 조건에 적합한지 확인"""
        try:
            # 자기 자신 제외
            if student.get('user_id') == current_id:
                return False
                
            # 같은 인스타그램 사용자 제외
            if student.get('instagram', '').replace('@', '') == current_instagram:
                return False
                
            # 학년 확인
            if target_grade:
                student_grade = student.get('grade')
                if isinstance(student_grade, str):
                    student_grade = int(student_grade.replace('학년', ''))
                if student_grade != target_grade:
                    return False
                    
            # 이미 매칭된 기록이 있는지 확인
            if self.get_existing_matching(current_id, student.get('user_id')):
                return False
                
            # MBTI 궁합 확인 (있으면 가중치 부여)
            student_mbti = student.get('mbti', '')
            if compatible_mbti_types and student_mbti in compatible_mbti_types:
                student['weight'] = 2  # MBTI 궁합이 맞으면 가중치 2
            else:
                student['weight'] = 1  # 기본 가중치 1
                
            return True
            
        except Exception as e:
            print(f"사용자 적합성 확인 중 오류 발생: {str(e)}")
            traceback.print_exc()
            return False 

    def get_user_by_credentials(self, nickname, instagram, name):
        """사용자 인증 정보로 사용자 조회 (별명과 인스타그램 아이디로 식별)"""
        try:
            print("\n=== 사용자 인증 시작 ===")
            print(f"검색 조건: nickname='{nickname}', instagram='{instagram}'")
            
            if self.test_mode:
                print("테스트 모드에서 실행 중")
                for user in self.test_data['students']:
                    if (user.get('nickname', '').lower() == nickname.lower() and
                        user.get('instagram', '').lower() == instagram.lower()):
                        print(f"테스트 모드: 일치하는 사용자 찾음 - {user}")
                        return user
                print("테스트 모드: 일치하는 사용자 없음")
                return None
            
            # Firestore에서 조회
            print("\nFirestore 검색 시작...")
            
            # 1. 먼저 모든 사용자를 가져와서 로컬에서 필터링
            all_users = self.db.collection('students').stream()
            matching_users = []
            
            for doc in all_users:
                user_data = doc.to_dict()
                user_data['user_id'] = doc.id
                
                stored_nickname = user_data.get('nickname', '').lower()
                stored_instagram = user_data.get('instagram', '').lower()
                
                print(f"\n검사 중인 사용자:")
                print(f"- Stored nickname: '{stored_nickname}' (입력값: '{nickname.lower()}')")
                print(f"- Stored instagram: '{stored_instagram}' (입력값: '{instagram.lower()}')")
                
                if (stored_nickname == nickname.lower() and
                    stored_instagram == instagram.lower()):
                    print("=> 일치하는 사용자 발견!")
                    matching_users.append(user_data)
            
            if matching_users:
                if len(matching_users) > 1:
                    print(f"\n주의: 중복된 사용자 발견 ({len(matching_users)}명)")
                print(f"\n찾은 사용자 정보: {matching_users[0]}")
                return matching_users[0]
            
            print("\n일치하는 사용자를 찾지 못했습니다.")
            return None
            
        except Exception as e:
            print(f"\n사용자 조회 중 오류 발생: {str(e)}")
            traceback.print_exc()
            return None 