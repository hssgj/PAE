"""Validated, declarative model drawers; no network, downloads or rotation."""
from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

DEFAULT_PROFILES = Path(__file__).resolve().parent.parent / 'config' / 'model_profiles.json'
PROFILE_ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$')
ENV_NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
FIELDS = {'provider','url','model','model_env','context_tokens','max_output_tokens','disable_thinking','api_key_env','api_key_file','verification'}


class ProfileError(ValueError):
    pass


@dataclass(frozen=True)
class ModelProfile:
    profile_id: str
    provider: str
    url: str = ''
    model: str = ''
    model_env: str = ''
    context_tokens: int = 0
    max_output_tokens: int = 0
    disable_thinking: bool = False
    api_key_env: str = ''
    api_key_file: str = ''
    verification: str = 'unverified'

    def summary(self) -> dict:
        return {'profile':self.profile_id,'provider':self.provider,'model':self.model or None,
                'model_reference':self.model_env or None,
                'context_tokens':self.context_tokens or None,'max_output_tokens':self.max_output_tokens or None,
                'verification':self.verification}

    def resolve_model(self) -> str:
        value = os.environ.get(self.model_env, '').strip() if self.model_env else self.model
        if not value or any(c.isspace() for c in value):
            raise ProfileError(f'Verified model ID is required for profile {self.profile_id}')
        return value

    def resolve_key(self) -> str:
        """Resolve only the explicitly selected profile's credential reference."""
        if not self.api_key_env and not self.api_key_file:
            return ''
        key = os.environ.get(self.api_key_env, '').strip() if self.api_key_env else ''
        if not key and self.api_key_file:
            path = Path(self.api_key_file).expanduser()
            try:
                if path.stat().st_size > 16384:
                    raise ProfileError('Credential file exceeds size limit')
                key = path.read_text(encoding='utf-8').strip()
            except (OSError, UnicodeError):
                raise ProfileError(f'Credential unavailable for profile {self.profile_id}') from None
        if not key or len(key) > 16384 or any(char.isspace() for char in key):
            raise ProfileError(f'Credential unavailable or malformed for profile {self.profile_id}')
        return key


def _validate(profile_id: str, data: object) -> ModelProfile:
    if not PROFILE_ID.fullmatch(profile_id) or not isinstance(data, dict):
        raise ProfileError('Invalid profile identifier or profile object')
    if set(data) - FIELDS:
        raise ProfileError(f'Unsupported fields in profile {profile_id}; store credential references only')
    for key in ('provider','url','model','model_env','api_key_env','api_key_file','verification'):
        if key in data and (not isinstance(data[key], str) or not data[key].strip()):
            raise ProfileError(f'{key} must be non-empty text in profile {profile_id}')
    provider = data.get('provider')
    if provider not in {'echo','openai-compatible'}:
        raise ProfileError(f'Unsupported provider in profile {profile_id}')
    if provider == 'echo':
        if set(data) - {'provider','verification'}:
            raise ProfileError('Echo profile accepts no model or credential configuration')
        return ModelProfile(profile_id=profile_id, **data)
    for key in ('url','context_tokens','max_output_tokens'):
        if key not in data:
            raise ProfileError(f'{key} is required in profile {profile_id}')
    if ('model' in data) == ('model_env' in data):
        raise ProfileError('Choose exactly one model ID or model environment reference')
    if data.get('model_env') and not ENV_NAME.fullmatch(data['model_env']):
        raise ProfileError('Invalid model environment variable name')
    for key in ('context_tokens','max_output_tokens'):
        if type(data[key]) is not int or data[key] <= 0:
            raise ProfileError(f'{key} must be a positive integer in profile {profile_id}')
    if data['max_output_tokens'] >= data['context_tokens']:
        raise ProfileError('Output token limit must be below declared context capacity')
    if type(data.get('disable_thinking', False)) is not bool:
        raise ProfileError('disable_thinking must be boolean')
    try:
        url = urlsplit(data['url'])
        _ = url.port
        if url.scheme not in {'https','http'} or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise ValueError
        if url.scheme == 'http':
            try:
                loopback = ipaddress.ip_address(url.hostname).is_loopback
            except ValueError:
                loopback = url.hostname == 'localhost'
            if not loopback:
                raise ValueError
    except ValueError:
        raise ProfileError('Endpoint must be HTTPS or loopback HTTP, without embedded credentials or query') from None
    env = data.get('api_key_env', '')
    if env and not ENV_NAME.fullmatch(env):
        raise ProfileError('Invalid credential environment variable name')
    return ModelProfile(profile_id=profile_id, **data)


def load_profiles(path: str | Path | None = None) -> dict[str, ModelProfile]:
    source = Path(path or os.getenv('PAE_PROFILES_FILE') or DEFAULT_PROFILES).expanduser()
    try:
        if source.stat().st_size > 1_000_000:
            raise ProfileError('Profile catalog exceeds size limit')
        def unique_keys(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ProfileError('Duplicate key in model profile catalog')
                result[key] = value
            return result
        data = json.loads(source.read_text(encoding='utf-8'), object_pairs_hook=unique_keys)
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ProfileError('Profile catalog unavailable or invalid JSON') from None
    if not isinstance(data, dict) or set(data) != {'schema_version','profiles'} or type(data['schema_version']) is not int or data['schema_version'] != 1:
        raise ProfileError('Unsupported profile catalog schema')
    if not isinstance(data['profiles'], dict) or not data['profiles']:
        raise ProfileError('Profile catalog must contain profiles')
    return {name:_validate(name, values) for name, values in data['profiles'].items()}


def get_profile(name: str, path: str | Path | None = None) -> ModelProfile:
    profiles = load_profiles(path)
    if name not in profiles:
        raise ProfileError('Unknown model profile; no fallback was selected')
    return profiles[name]
