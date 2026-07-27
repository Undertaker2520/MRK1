from tools_system import (
    open_application, close_application, open_file, 
    lock_pc, unlock_pc, suspend_pc, shutdown_pc, restart_pc
)
from tools_hardware import (
    screen_shot, analyze_screen, volume_control, brightness_control, 
    get_system_status, get_tactical_briefing
)
from tools_web import search_web, play_youtube_video, media_control, read_clipboard, set_timer
from tools_protocols import protocol_work, protocol_gaming, protocol_night
from config_manager import update_protocol_preferences
from tools_projects import register_project, launch_project
from tools_ide import send_prompt_to_ide_ai

AVAILABLE_TOOLS = {
    # System & Power Tools
    'open_application': open_application,
    'close_application': close_application,
    'open_file': open_file,
    'lock_pc': lock_pc,
    'unlock_pc': unlock_pc,
    'suspend_pc': suspend_pc,
    'shutdown_pc': shutdown_pc,
    'restart_pc': restart_pc,
    
    # Hardware, Telemetry & Vision Tools
    'screen_shot': screen_shot,
    'analyze_screen': analyze_screen,
    'volume_control': volume_control,
    'brightness_control': brightness_control,
    'get_system_status': get_system_status,
    'get_tactical_briefing': get_tactical_briefing,
    
    # Web & Utility Tools
    'search_web': search_web,
    'play_youtube_video': play_youtube_video,
    'media_control': media_control,
    'read_clipboard': read_clipboard,
    'set_timer': set_timer,
    
    # Protocols & Preferences
    'protocol_work': protocol_work,
    'protocol_gaming': protocol_gaming,
    'protocol_night': protocol_night,
    'update_protocol_preferences': update_protocol_preferences,
    
    # Project Manager
    'register_project': register_project,
    'launch_project': launch_project,
    
    # IDE AI Integration
    'send_prompt_to_ide_ai': send_prompt_to_ide_ai
}

TOOLS_LIST = list(AVAILABLE_TOOLS.values())