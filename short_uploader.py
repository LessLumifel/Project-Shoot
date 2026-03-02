import argparse
import json
import os
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ShortPayload:
    video_path: str
    title: str
    description: str
    hashtags: List[str]
    privacy: Dict[str, str]


class BaseUploader:
    platform_name: str

    def __init__(self, config: Dict[str, str]):
        self.config = config

    def upload(self, payload: ShortPayload) -> Dict[str, str]:
        raise NotImplementedError

    @staticmethod
    def _build_caption(payload: ShortPayload) -> str:
        tags = " ".join(payload.hashtags)
        return f"{payload.description}\n\n{tags}".strip()


class FacebookUploader(BaseUploader):
    platform_name = "facebook"

    def upload(self, payload: ShortPayload) -> Dict[str, str]:
        return {
            "endpoint": f"https://graph.facebook.com/v20.0/{self.config['page_id']}/video_reels",
            "method": "POST",
            "note": "Template only: integrate real multipart upload + token handling",
            "payload_preview": {
                "description": self._build_caption(payload),
                "published": True,
            },
        }


class YouTubeUploader(BaseUploader):
    platform_name = "youtube"

    def upload(self, payload: ShortPayload) -> Dict[str, str]:
        return {
            "endpoint": "https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status&uploadType=resumable",
            "method": "POST",
            "note": "Template only: integrate resumable upload flow",
            "payload_preview": {
                "snippet": {
                    "title": payload.title,
                    "description": self._build_caption(payload),
                },
                "status": {
                    "privacyStatus": payload.privacy.get("youtube", "private"),
                },
            },
        }


class TikTokUploader(BaseUploader):
    platform_name = "tiktok"

    def upload(self, payload: ShortPayload) -> Dict[str, str]:
        return {
            "endpoint": "https://open.tiktokapis.com/v2/post/publish/video/init/",
            "method": "POST",
            "note": "Template only: call init endpoint then upload chunks to returned upload_url",
            "payload_preview": {
                "post_info": {
                    "title": payload.title,
                    "privacy_level": payload.privacy.get("tiktok", "PUBLIC_TO_EVERYONE"),
                },
                "source_info": {
                    "video_size": os.path.getsize(payload.video_path),
                    "total_chunk_count": 1,
                },
            },
        }


def load_payload(path: str) -> ShortPayload:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ShortPayload(**data)


def build_uploaders(config: Dict[str, Dict[str, str]], platforms: List[str]) -> List[BaseUploader]:
    all_uploaders = {
        "facebook": FacebookUploader,
        "youtube": YouTubeUploader,
        "tiktok": TikTokUploader,
    }
    uploaders: List[BaseUploader] = []
    for p in platforms:
        key = p.strip().lower()
        if key not in all_uploaders:
            raise ValueError(f"Unsupported platform: {p}")
        if key not in config:
            raise ValueError(f"Missing config section: {key}")
        uploaders.append(all_uploaders[key](config[key]))
    return uploaders


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload short clips to multiple platforms")
    parser.add_argument("--config", required=True, help="Path to config JSON")
    parser.add_argument("--payload", required=True, help="Path to payload JSON")
    parser.add_argument("--platforms", required=True, help="Comma-separated platforms, e.g. facebook,youtube,tiktok")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    payload = load_payload(args.payload)

    if not os.path.exists(payload.video_path):
        raise FileNotFoundError(f"Video file not found: {payload.video_path}")

    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
    uploaders = build_uploaders(config, platforms)

    results = {}
    for uploader in uploaders:
        try:
            results[uploader.platform_name] = {
                "status": "ready",
                "request_template": uploader.upload(payload),
            }
        except Exception as exc:
            results[uploader.platform_name] = {
                "status": "failed",
                "error": str(exc),
            }

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
