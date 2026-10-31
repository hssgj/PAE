import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from model_profiles import ProfileError, get_profile, load_profiles
from provider import EchoProvider, build_provider


class ModelProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'profiles.json'
        self.local = {'provider':'openai-compatible','url':'http://127.0.0.1:8080/v1/chat/completions','model':'fixture','context_tokens':1024,'max_output_tokens':77,'disable_thinking':True}

    def catalog(self, value):
        self.path.write_text(json.dumps({'schema_version':1,'profiles':value}))
        return self.path

    def test_default_catalog_has_expected_drawers_and_no_secret_values(self):
        profiles = load_profiles()
        self.assertEqual(set(profiles), {'echo','local-qwen','groq','gemini'})
        self.assertEqual(profiles['gemini'].verification, 'prepared_verified_model_id_required')
        self.assertEqual(profiles['gemini'].model, '')
        self.assertNotIn('api_key', profiles['groq'].summary())

    def test_explicit_profile_isolated_from_legacy_environment(self):
        with patch.dict(os.environ, {'PAE_PROVIDER':'broken','PAE_API_KEY':'do-not-send','PAE_MAX_TOKENS':'999','PAE_DISABLE_THINKING':'0'}, clear=True):
            provider = build_provider(profile_name='local', profiles_path=self.catalog({'local':self.local}))
        self.assertEqual(provider.api_key, '')
        self.assertEqual(provider.max_tokens, 77)
        self.assertTrue(provider.disable_thinking)
        self.assertEqual(provider.profile_id, 'local')

    def test_unknown_or_empty_profile_fails_without_echo_fallback(self):
        self.catalog({'echo':{'provider':'echo'}})
        with self.assertRaises(ProfileError):
            build_provider(profile_name='missing', profiles_path=self.path)
        with self.assertRaises(ProfileError):
            build_provider(profile_name='', profiles_path=self.path)

    def test_listing_does_not_read_credentials(self):
        data={**self.local,'api_key_file':str(Path(self.temp.name)/'missing.key')}
        summaries=[p.summary() for p in load_profiles(self.catalog({'cloud':data})).values()]
        self.assertEqual(summaries[0]['profile'],'cloud')
        with self.assertRaises(ProfileError):
            build_provider(profile_name='cloud',profiles_path=self.path)

    def test_credential_reference_resolves_only_selected_profile(self):
        key=Path(self.temp.name)/'credential.key';key.write_text('fixture-secret\n')
        profiles={'local':self.local,'cloud':{**self.local,'api_key_env':'FIXTURE_KEY','api_key_file':str(key)}}
        with patch.dict(os.environ, {'FIXTURE_KEY':'environment-secret'}, clear=True):
            provider=build_provider(profile_name='cloud',profiles_path=self.catalog(profiles))
        self.assertEqual(provider.api_key,'environment-secret')
        with patch.dict(os.environ, {}, clear=True):
            provider=build_provider(profile_name='cloud',profiles_path=self.path)
        self.assertEqual(provider.api_key,'fixture-secret')
        self.assertNotIn('fixture-secret',str(get_profile('cloud',self.path).summary()))

    def test_profile_rejects_literal_keys_unknown_fields_and_bad_limits(self):
        variants=[{**self.local,'api_key':'literal'}, {**self.local,'typo':1}, {**self.local,'context_tokens':True}, {**self.local,'max_output_tokens':1024}, {**self.local,'disable_thinking':'yes'}]
        for variant in variants:
            with self.subTest(variant=list(variant)):
                with self.assertRaises(ProfileError): load_profiles(self.catalog({'invalid':variant}))

    def test_insecure_remote_or_credential_bearing_endpoint_rejected(self):
        for url in ['http://example.com/v1/chat/completions','https://user:password@example.com/v1','https://example.com/v1?key=private','https://example.com/v1#fragment']:
            with self.subTest(url=url):
                with self.assertRaises(ProfileError): load_profiles(self.catalog({'invalid':{**self.local,'url':url}}))

    def test_duplicate_json_keys_rejected(self):
        self.path.write_text('{"schema_version":1,"profiles":{"echo":{"provider":"echo"},"echo":{"provider":"echo"}}}')
        with self.assertRaises(ProfileError): load_profiles(self.path)

    def test_profile_config_is_applied_to_actual_request_payload(self):
        provider=build_provider(profile_name='local',profiles_path=self.catalog({'local':self.local}))
        seen=[]
        def fake_open(req, **kwargs):
            seen.append(req)
            return io.BytesIO(json.dumps({'choices':[{'message':{'content':'response'}}]}).encode())
        with patch('provider.request.urlopen', side_effect=fake_open):
            self.assertEqual(provider.chat([{'role':'user','content':'ping'}]),'response')
        body=json.loads(seen[0].data)
        self.assertEqual(body['model'],'fixture')
        self.assertEqual(body['max_tokens'],77)
        self.assertEqual(body['chat_template_kwargs'],{'enable_thinking':False})
        self.assertEqual(seen[0].get_header('User-agent'),'PAE/0.1')
        self.assertIsNone(seen[0].get_header('Authorization'))

    def test_no_profile_retains_legacy_factory(self):
        with patch.dict(os.environ, {'PAE_PROVIDER':'echo'}, clear=True):
            self.assertIsInstance(build_provider(),EchoProvider)

    def test_missing_model_reference_fails_before_credentials_or_request(self):
        data={k:v for k,v in self.local.items() if k!='model'}
        data['model_env']='VERIFIED_MODEL_ID'
        self.catalog({'pending':data})
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(ProfileError): build_provider(profile_name='pending',profiles_path=self.path)
        with patch.dict(os.environ,{'VERIFIED_MODEL_ID':'selected-model'},clear=True):
            self.assertEqual(build_provider(profile_name='pending',profiles_path=self.path).model,'selected-model')


if __name__ == '__main__':
    unittest.main()
