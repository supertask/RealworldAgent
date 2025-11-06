"""Mock Data for RealworldAgent Frontend"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# プロジェクトデータ
mock_projects = [
    {
        'id': 'project-alpha-001',
        'name': 'ProjectAlpha',
        'description': 'eコマースプラットフォームの開発',
        'status': 'active',
        'repository_url': 'https://github.com/supertask/ProjectAlpha',
        'cursor_sessions': {
            'frontend': [
                {
                    'session_id': 'session_alpha_frontend_001',
                    'created_at': '2024-10-27T14:00:00Z',
                    'last_used': '2024-10-27T15:25:00Z',
                    'documents_processed': 1,
                    'status': 'active',
                    'closed_at': None,
                    'closed_reason': None
                },
                {
                    'session_id': 'session_alpha_frontend_000',
                    'created_at': '2024-10-15T10:00:00Z',
                    'last_used': '2024-10-26T18:00:00Z',
                    'documents_processed': 8,
                    'status': 'closed',
                    'closed_at': '2024-10-26T18:00:00Z',
                    'closed_reason': 'Manually closed - context refresh'
                }
            ],
            'backend': [
                {
                    'session_id': 'session_alpha_backend_001',
                    'created_at': '2024-10-28T15:00:00Z',
                    'last_used': '2024-10-28T15:00:00Z',
                    'documents_processed': 0,
                    'status': 'active',
                    'closed_at': None,
                    'closed_reason': None
                }
            ],
            'test': [
                {
                    'session_id': 'session_alpha_test_001',
                    'created_at': '2024-10-25T12:00:00Z',
                    'last_used': '2024-10-25T13:15:00Z',
                    'documents_processed': 1,
                    'status': 'active',
                    'closed_at': None,
                    'closed_reason': None
                }
            ],
            'all': [
                {
                    'session_id': 'session_alpha_all_001',
                    'created_at': '2024-10-24T09:00:00Z',
                    'last_used': '2024-10-24T11:30:00Z',
                    'documents_processed': 1,
                    'status': 'active',
                    'closed_at': None,
                    'closed_reason': None
                }
            ]
        },
        'created_at': '2024-10-15T10:00:00Z',
        'last_updated': '2024-10-28T15:30:00Z',
        'meeting_count': 8,
        'document_count': 12,
        'pr_count': 15
    },
    {
        'id': 'project-beta-002',
        'name': 'ProjectBeta',
        'description': 'AIチャットボットシステム',
        'status': 'active',
        'repository_url': 'https://github.com/supertask/ProjectBeta',
        'cursor_sessions': {
            'frontend': [
                {
                    'session_id': 'session_beta_frontend_001',
                    'created_at': '2024-10-26T10:00:00Z',
                    'last_used': '2024-10-26T11:45:00Z',
                    'documents_processed': 1,
                    'status': 'active',
                    'closed_at': None,
                    'closed_reason': None
                }
            ],
            'backend': [
                {
                    'session_id': 'session_beta_backend_001',
                    'created_at': '2024-10-22T16:00:00Z',
                    'last_used': '2024-10-22T17:20:00Z',
                    'documents_processed': 1,
                    'status': 'active',
                    'closed_at': None,
                    'closed_reason': None
                }
            ],
            'management': [
                {
                    'session_id': 'session_beta_management_001',
                    'created_at': '2024-10-23T13:00:00Z',
                    'last_used': '2024-10-23T14:00:00Z',
                    'documents_processed': 1,
                    'status': 'active',
                    'closed_at': None,
                    'closed_reason': None
                }
            ]
        },
        'created_at': '2024-10-20T14:00:00Z',
        'last_updated': '2024-10-27T18:45:00Z',
        'meeting_count': 5,
        'document_count': 7,
        'pr_count': 9
    },
    {
        'id': 'project-gamma-003',
        'name': 'ProjectGamma',
        'description': 'データ分析ダッシュボード',
        'status': 'active',
        'repository_url': 'https://github.com/supertask/ProjectGamma',
        'cursor_sessions': {
            'frontend': [
                {
                    'session_id': 'session_gamma_frontend_001',
                    'created_at': '2024-10-26T10:30:00Z',
                    'last_used': '2024-10-26T11:15:00Z',
                    'documents_processed': 1,
                    'status': 'active',
                    'closed_at': None,
                    'closed_reason': None
                }
            ]
        },
        'created_at': '2024-10-25T09:00:00Z',
        'last_updated': '2024-10-26T12:00:00Z',
        'meeting_count': 2,
        'document_count': 3,
        'pr_count': 1
    }
]

# ミーティングデータ
mock_meetings = [
    {
        'id': 'meet_abc123',
        'project_id': 'project-alpha-001',
        'project_name': 'ProjectAlpha',
        'meeting_name': 'ProjectAlpha_frontend_LoginUI',
        'scope': 'frontend',
        'title': 'LoginUI',
        'meeting_type': 'online',
        'device_type': None,
        'date': '2024-10-27T14:00:00Z',
        'duration': '45分',
        'status': 'completed',
        'processing_time': '8分',
        'recording_url': 'https://drive.google.com/file/d/abc123',
        'transcript_url': 'https://docs.google.com/document/d/abc123',
        'github_doc_url': 'https://github.com/supertask/ProjectAlpha/blob/main/frontend/Docs/Doc-meet_abc123-20241027_140000.md',
        'screenshot_count': 12
    },
    {
        'id': 'meet_def456',
        'project_id': 'project-alpha-001',
        'project_name': 'ProjectAlpha',
        'meeting_name': 'ProjectAlpha_backend_AuthAPI',
        'scope': 'backend',
        'title': 'AuthAPI',
        'meeting_type': 'online',
        'device_type': None,
        'date': '2024-10-28T15:00:00Z',
        'duration': '30分',
        'status': 'processing',
        'processing_time': '進行中',
        'recording_url': 'https://drive.google.com/file/d/def456',
        'transcript_url': None,
        'github_doc_url': None,
        'screenshot_count': 0,
        'processing_step': 'video_analysis',
        'processing_progress': 65
    },
    {
        'id': 'meet_ghi789',
        'project_id': 'project-beta-002',
        'project_name': 'ProjectBeta',
        'meeting_name': 'ProjectBeta_frontend_ChatWidget',
        'scope': 'frontend',
        'title': 'ChatWidget',
        'meeting_type': 'online',
        'device_type': None,
        'date': '2024-10-26T10:00:00Z',
        'duration': '60分',
        'status': 'completed',
        'processing_time': '7分',
        'recording_url': 'https://drive.google.com/file/d/ghi789',
        'transcript_url': 'https://docs.google.com/document/d/ghi789',
        'github_doc_url': 'https://github.com/supertask/ProjectBeta/blob/main/frontend/Docs/Doc-meet_ghi789-20241026_100000.md',
        'screenshot_count': 18
    }
]

# コード生成データ
mock_code_generation = [
    {
        'id': 'codegen_001',
        'project_id': 'project-alpha-001',
        'project_name': 'ProjectAlpha',
        'meeting_id': 'meet_abc123',
        'meeting_name': 'ProjectAlpha_frontend_LoginUI',
        'scope': 'frontend',
        'document_id': 'doc_abc123',
        'status': 'completed',
        'cursor_session_id': 'session_alpha_frontend_001',
        'started_at': '2024-10-27T14:50:00Z',
        'completed_at': '2024-10-27T15:25:00Z',
        'pr_url': 'https://github.com/supertask/ProjectAlpha/pull/123',
        'pr_number': 123,
        'pr_status': 'merged',
        'pr_merged_at': '2024-10-27T18:00:00Z',
        'files_generated': [
            {'path': 'frontend/src/components/LoginForm.tsx', 'lines_added': 150, 'lines_deleted': 0},
            {'path': 'frontend/src/services/authService.ts', 'lines_added': 85, 'lines_deleted': 12},
            {'path': 'frontend/src/types/auth.types.ts', 'lines_added': 45, 'lines_deleted': 0}
        ],
        'logs': [
            {'timestamp': '14:50:15', 'level': 'info', 'message': 'Cursor Agent セッション開始'},
            {'timestamp': '14:51:30', 'level': 'info', 'message': '仕様書解析完了 (scope: frontend)'},
            {'timestamp': '15:25:00', 'level': 'success', 'message': 'コード生成完了'}
        ]
    },
    {
        'id': 'codegen_002',
        'project_id': 'project-beta-002',
        'project_name': 'ProjectBeta',
        'meeting_id': 'meet_ghi789',
        'meeting_name': 'ProjectBeta_frontend_ChatWidget',
        'scope': 'frontend',
        'document_id': 'doc_ghi789',
        'status': 'processing',
        'cursor_session_id': 'session_beta_frontend_001',
        'started_at': '2024-10-26T11:30:00Z',
        'completed_at': None,
        'pr_url': None,
        'pr_number': None,
        'pr_status': None,
        'pr_merged_at': None,
        'files_generated': [
            {'path': 'frontend/src/components/ChatWidget.tsx', 'lines_added': 120, 'lines_deleted': 0}
        ],
        'logs': [
            {'timestamp': '11:30:15', 'level': 'info', 'message': 'Cursor Agent セッション開始'},
            {'timestamp': '11:35:00', 'level': 'info', 'message': 'frontend/src/components/ChatWidget.tsx 生成中...'}
        ]
    }
]

# Pull Request データ
mock_pull_requests = [
    {
        'id': 'pr_123',
        'project_id': 'project-alpha-001',
        'project_name': 'ProjectAlpha',
        'meeting_id': 'meet_abc123',
        'meeting_name': 'ProjectAlpha_frontend_LoginUI',
        'scope': 'frontend',
        'number': 123,
        'title': 'feat(frontend): ログイン機能実装',
        'description': 'Google Meetミーティング (Doc-meet_abc123-20241027_140000.md) の仕様に基づいてログイン機能を実装',
        'status': 'merged',
        'branch': 'frontend/feature/update-from-meet_abc123',
        'url': 'https://github.com/supertask/ProjectAlpha/pull/123',
        'created_at': '2024-10-27T15:30:00Z',
        'merged_at': '2024-10-27T18:00:00Z',
        'files_changed': 3,
        'additions': 280,
        'deletions': 12,
        'commits': 1
    },
    {
        'id': 'pr_124',
        'project_id': 'project-alpha-001',
        'project_name': 'ProjectAlpha',
        'meeting_id': None,
        'meeting_name': None,
        'scope': 'frontend',
        'number': 124,
        'title': 'feat(frontend): パスワードリセット機能',
        'description': 'ユーザーがパスワードを忘れた場合のリセット機能を追加',
        'status': 'open',
        'branch': 'frontend/feature/password-reset',
        'url': 'https://github.com/supertask/ProjectAlpha/pull/124',
        'created_at': '2024-10-28T10:00:00Z',
        'merged_at': None,
        'files_changed': 5,
        'additions': 350,
        'deletions': 8,
        'commits': 2
    },
    {
        'id': 'pr_45',
        'project_id': 'project-beta-002',
        'project_name': 'ProjectBeta',
        'meeting_id': 'meet_ghi789',
        'meeting_name': 'ProjectBeta_frontend_ChatWidget',
        'scope': 'frontend',
        'number': 45,
        'title': 'feat(frontend): チャットウィジェットUI実装',
        'description': 'Google Meetミーティング (Doc-meet_ghi789-20241026_100000.md) で設計したUIを実装',
        'status': 'open',
        'branch': 'frontend/feature/update-from-meet_ghi789',
        'url': 'https://github.com/supertask/ProjectBeta/pull/45',
        'created_at': '2024-10-26T11:45:00Z',
        'merged_at': None,
        'files_changed': 8,
        'additions': 520,
        'deletions': 45,
        'commits': 1
    }
]

# 通知データ
mock_notifications = [
    {
        'id': 'notif_001',
        'type': 'meeting_detected',
        'title': '新しいミーティングを検出',
        'message': 'ProjectAlpha_backend_AuthAPI',
        'timestamp': '2024-10-28T15:05:00Z',
        'read': False,
        'link': '/meetings?id=meet_def456'
    },
    {
        'id': 'notif_002',
        'type': 'pr_created',
        'title': 'Pull Request作成完了',
        'message': 'ProjectAlpha #123: feat(frontend): ログイン機能実装',
        'timestamp': '2024-10-27T15:30:00Z',
        'read': False,
        'link': '/code-generation?id=pr_123'
    },
    {
        'id': 'notif_003',
        'type': 'pr_merged',
        'title': 'Pull Requestがマージされました',
        'message': 'ProjectAlpha #123: feat(frontend): ログイン機能実装',
        'timestamp': '2024-10-27T18:00:00Z',
        'read': True,
        'link': '/code-generation?id=pr_123'
    }
]


class MockDataHelpers:
    """モックデータのヘルパー関数クラス"""
    
    @staticmethod
    def get_project_by_id(project_id: str) -> Optional[Dict]:
        """プロジェクトIDからプロジェクトを取得"""
        return next((p for p in mock_projects if p['id'] == project_id), None)
    
    @staticmethod
    def get_meetings_by_project(project_id: str) -> List[Dict]:
        """プロジェクトIDに紐づくミーティングを取得"""
        return [m for m in mock_meetings if m['project_id'] == project_id]
    
    @staticmethod
    def get_recent_meetings(limit: int = 5) -> List[Dict]:
        """最近のミーティングを取得（日付降順）"""
        sorted_meetings = sorted(mock_meetings, key=lambda m: m['date'], reverse=True)
        return sorted_meetings[:limit]
    
    @staticmethod
    def get_unread_notifications() -> List[Dict]:
        """未読通知を取得"""
        return [n for n in mock_notifications if not n['read']]
    
    @staticmethod
    def get_processing_code_generation() -> List[Dict]:
        """処理中のコード生成を取得"""
        return [cg for cg in mock_code_generation if cg['status'] == 'processing']
    
    @staticmethod
    def format_relative_time(iso_string: str) -> str:
        """相対時間表示"""
        try:
            date = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            now = datetime.now(date.tzinfo)
            diff = now - date
            
            if diff < timedelta(minutes=1):
                return 'たった今'
            elif diff < timedelta(hours=1):
                return f'{int(diff.total_seconds() / 60)}分前'
            elif diff < timedelta(days=1):
                return f'{int(diff.total_seconds() / 3600)}時間前'
            elif diff < timedelta(days=7):
                return f'{diff.days}日前'
            else:
                return date.strftime('%Y年%m月%d日')
        except:
            return iso_string
    
    @staticmethod
    def format_datetime(iso_string: str) -> str:
        """日時フォーマット"""
        try:
            date = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            return date.strftime('%Y年%m月%d日 %H:%M')
        except:
            return iso_string
    
    @staticmethod
    def get_scope_display_name(scope: str) -> str:
        """scopeの表示名を取得"""
        scope_names = {
            'frontend': 'フロントエンド',
            'backend': 'バックエンド',
            'test': 'テスト',
            'all': '全体',
            'management': 'マネジメント'
        }
        return scope_names.get(scope, scope)
    
    @staticmethod
    def render_scope_badge(scope: str) -> str:
        """scopeバッジHTMLを生成"""
        display_name = MockDataHelpers.get_scope_display_name(scope)
        return f'<span class="scope-badge scope-badge-{scope}">{display_name}</span>'
    
    @staticmethod
    def get_meeting_type_display_name(meeting_type: str) -> str:
        """ミーティングタイプの表示名を取得"""
        return 'オンライン' if meeting_type == 'online' else '対面'

