"""Notification system for solved challenges"""

import requests
import json
from typing import Optional
from datetime import datetime

from core.config import Config
from core.challenge import ChallengeResult


class NotificationManager:
    """Send notifications for solved challenges"""
    
    def __init__(self, config: Config):
        self.config = config
        self.discord_webhook = config.get('notifications.discord.webhook_url', '')
        self.slack_webhook = config.get('notifications.slack.webhook_url', '')
    
    def notify(self, result: ChallengeResult):
        """Send notification for challenge result"""
        if not result.success:
            return
        
        if self.config.get('notifications.discord.enabled', False):
            self._notify_discord(result)
        
        if self.config.get('notifications.slack.enabled', False):
            self._notify_slack(result)
    
    def _notify_discord(self, result: ChallengeResult):
        """Send Discord notification"""
        if not self.discord_webhook:
            return
        
        embed = {
            "title": f"🚩 Challenge Solved: {result.challenge.name}",
            "color": 0x00ff00,
            "fields": [
                {"name": "Category", "value": result.challenge.category or "Unknown", "inline": True},
                {"name": "Points", "value": str(result.challenge.points), "inline": True},
                {"name": "Method", "value": result.method or "Unknown", "inline": True},
                {"name": "Duration", "value": f"{result.duration:.2f}s", "inline": True},
                {"name": "Flag", "value": f"||{result.flag}||", "inline": False},
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "MD-EXPLOIT-ENGINE"}
        }
        
        payload = {"embeds": [embed]}
        
        try:
            requests.post(self.discord_webhook, json=payload, timeout=10)
        except:
            pass
    
    def _notify_slack(self, result: ChallengeResult):
        """Send Slack notification"""
        if not self.slack_webhook:
            return
        
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"🚩 Challenge Solved: {result.challenge.name}"}
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Category:* {result.challenge.category or 'Unknown'}"},
                        {"type": "mrkdwn", "text": f"*Points:* {result.challenge.points}"},
                        {"type": "mrkdwn", "text": f"*Method:* {result.method or 'Unknown'}"},
                        {"type": "mrkdwn", "text": f"*Duration:* {result.duration:.2f}s"},
                    ]
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Flag:* `{result.flag}`"}
                }
            ]
        }
        
        try:
            requests.post(self.slack_webhook, json=payload, timeout=10)
        except:
            pass
    
    def send_summary(self, results: list):
        """Send summary notification"""
        solved = sum(1 for r in results if r.success)
        total = len(results)
        
        message = f"📊 CTF Summary: {solved}/{total} challenges solved"
        
        if self.discord_webhook:
            try:
                requests.post(self.discord_webhook, json={"content": message}, timeout=10)
            except:
                pass
        
        if self.slack_webhook:
            try:
                requests.post(self.slack_webhook, json={"text": message}, timeout=10)
            except:
                pass
