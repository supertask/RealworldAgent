"""Flask Application for RealworldAgent Mock Frontend"""
from flask import Flask, render_template, request
from data.mock_data import (
    mock_projects, mock_meetings, mock_code_generation,
    mock_pull_requests, mock_notifications, MockDataHelpers
)
from markupsafe import Markup

app = Flask(__name__)

# デバッグモードを有効化
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True


# カスタムフィルターの登録
@app.template_filter('format_datetime')
def format_datetime_filter(iso_string):
    """日時フォーマットフィルター"""
    return MockDataHelpers.format_datetime(iso_string)


@app.template_filter('format_relative_time')
def format_relative_time_filter(iso_string):
    """相対時間表示フィルター"""
    return MockDataHelpers.format_relative_time(iso_string)


@app.template_filter('render_scope_badge')
def render_scope_badge_filter(scope):
    """scopeバッジHTMLを生成"""
    return Markup(MockDataHelpers.render_scope_badge(scope))


@app.template_filter('scope_display_name')
def scope_display_name_filter(scope):
    """scopeの表示名を取得"""
    return MockDataHelpers.get_scope_display_name(scope)


@app.template_filter('meeting_type_display')
def meeting_type_display_filter(meeting_type):
    """ミーティングタイプの表示名を取得"""
    return MockDataHelpers.get_meeting_type_display_name(meeting_type)


# ルート定義
@app.route('/')
@app.route('/dashboard')
def dashboard():
    """ダッシュボードページ"""
    return render_template(
        'dashboard.html',
        active_page='dashboard',
        projects=mock_projects,
        recent_meetings=MockDataHelpers.get_recent_meetings(3),
        processing_code_gens=MockDataHelpers.get_processing_code_generation(),
        recent_prs=mock_pull_requests[:3],
        notifications=mock_notifications,
        unread_count=len(MockDataHelpers.get_unread_notifications())
    )


@app.route('/projects')
def projects():
    """プロジェクト一覧ページ"""
    return render_template(
        'projects.html',
        active_page='projects',
        projects=mock_projects,
        notifications=mock_notifications,
        unread_count=len(MockDataHelpers.get_unread_notifications())
    )


@app.route('/project/<project_id>')
def project_detail(project_id):
    """プロジェクト詳細ページ"""
    project = MockDataHelpers.get_project_by_id(project_id)
    if not project:
        return "Project not found", 404
    
    meetings = MockDataHelpers.get_meetings_by_project(project_id)
    prs = [pr for pr in mock_pull_requests if pr['project_id'] == project_id]
    
    return render_template(
        'project_detail.html',
        active_page='projects',
        project=project,
        meetings=meetings,
        prs=prs,
        notifications=mock_notifications,
        unread_count=len(MockDataHelpers.get_unread_notifications())
    )


@app.route('/meetings')
def meetings():
    """ミーティング一覧ページ"""
    # フィルター処理
    status_filter = request.args.get('status', 'all')
    scope_filter = request.args.get('scope', 'all_scopes')
    type_filter = request.args.get('type', 'all_types')
    
    filtered_meetings = mock_meetings
    
    if status_filter != 'all':
        filtered_meetings = [m for m in filtered_meetings if m['status'] == status_filter]
    
    if scope_filter != 'all_scopes':
        filtered_meetings = [m for m in filtered_meetings if m['scope'] == scope_filter]
    
    if type_filter != 'all_types':
        filtered_meetings = [m for m in filtered_meetings if m['meeting_type'] == type_filter]
    
    return render_template(
        'meetings.html',
        active_page='meetings',
        meetings=filtered_meetings,
        all_meetings=mock_meetings,
        status_filter=status_filter,
        scope_filter=scope_filter,
        type_filter=type_filter,
        notifications=mock_notifications,
        unread_count=len(MockDataHelpers.get_unread_notifications())
    )


@app.route('/meeting/<meeting_id>')
def meeting_detail(meeting_id):
    """ミーティング詳細ページ"""
    meeting = next((m for m in mock_meetings if m['id'] == meeting_id), None)
    if not meeting:
        return "Meeting not found", 404
    
    # 関連するコード生成を取得
    related_code_gen = next((cg for cg in mock_code_generation if cg['meeting_id'] == meeting_id), None)
    
    # 関連するPRを取得
    related_prs = [pr for pr in mock_pull_requests if pr['meeting_id'] == meeting_id]
    
    return render_template(
        'meeting_detail.html',
        active_page='meetings',
        meeting=meeting,
        code_gen=related_code_gen,
        prs=related_prs,
        notifications=mock_notifications,
        unread_count=len(MockDataHelpers.get_unread_notifications())
    )


@app.route('/code-generation')
def code_generation():
    """コード生成状況ページ"""
    scope_filter = request.args.get('scope', 'all_scopes')
    project_filter = request.args.get('project', 'project-alpha-001')
    
    filtered_code_gen = mock_code_generation
    
    if project_filter:
        filtered_code_gen = [cg for cg in filtered_code_gen if cg['project_id'] == project_filter]
    
    if scope_filter != 'all_scopes':
        filtered_code_gen = [cg for cg in filtered_code_gen if cg['scope'] == scope_filter]
    
    return render_template(
        'code_generation.html',
        active_page='code_generation',
        code_generations=filtered_code_gen,
        scope_filter=scope_filter,
        project_filter=project_filter,
        notifications=mock_notifications,
        unread_count=len(MockDataHelpers.get_unread_notifications())
    )


@app.route('/settings')
def settings():
    """設定ページ"""
    return render_template(
        'settings.html',
        active_page='settings',
        notifications=mock_notifications,
        unread_count=len(MockDataHelpers.get_unread_notifications())
    )


if __name__ == '__main__':
    print("=" * 60)
    print("RealworldAgent Mock Server")
    print("=" * 60)
    print("Server running at: http://localhost:5001")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)

