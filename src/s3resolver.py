# -*- coding: utf-8 -*-

import boto3
import botocore
import hashlib
import io
import logging
import urllib
import urlparse
import os
import pickle
import zlib

from loris_exception import ResolverException
from loris.resolver import _AbstractResolver

logger = logging.getLogger(__name__)

# IIIF で対応するイメージフォーマットの Content-Type と loris のフォーマット定義の変換テーブルを構築します。
__formats = (
	('gif', 'image/gif'),
	('jp2', 'image/jp2'),
	('jpg', 'image/jpeg'),
	('pdf', 'application/pdf'),
	('png', 'image/png'),
	('tif', 'image/tiff'),
	('webp', 'image/webp'),
)
FORMATS_BY_EXTENSION = dict(__formats)
FORMATS_BY_MEDIA_TYPE = dict([(f[1], f[0]) for f in __formats])

"""
S3 のオブジェクトに対してアクセスする Loris の Resolver クラス。
"""
class S3Resolver(_AbstractResolver):

    def __init__(self, config):
        super(S3Resolver, self).__init__(config)

        self._cache_dir = self.config.get('cache_dir', '/tmp')
        self._region_name = self.config.get('region_name', 'us-west-2')
        self._aws_access_key_id = self.config.get('aws_access_key_id', '')
        self._aws_secret_access_key = self.config.get('aws_secret_access_key', '')
        self._bucket_name = self.config.get('bucket_name', '')

        logger.debug('cache_dir: %s' % (self._cache_dir))
        logger.debug('region_name: %s' % (self._region_name))
        logger.debug('aws_access_key_id: %s' % (self._aws_access_key_id))
        logger.debug('aws_secret_access_key: %s' % (self._aws_secret_access_key))
        logger.debug('bucket_name: %s' % (self._bucket_name))

        self._createdir()

        self._s3 = boto3.resource(
            service_name = 's3',
            region_name = self._region_name,
            aws_access_key_id = self._aws_access_key_id,
            aws_secret_access_key = self._aws_secret_access_key,
        )
        self._bucket = self._s3.Bucket(self._bucket_name)

        logger.info('loaded s3 bucket (%s).' % self._bucket.name)

    def is_resolvable(self, ident):
        key = urllib.unquote(ident)

        cache_fp = self._get_key_from_file(key, '.info')

        logger.debug('is_resolvable (ident: %s, key: %s, cache_fp: %s).' % (ident, key, cache_fp))

        is_exists = False

        if (os.path.exists(cache_fp)):
            logger.debug('cache exists (cache_fp: %s).' % (cache_fp))

            is_exists = True
        else:
            try:
                self._bucket.Object(key).load()

                is_exists = True
            except botocore.exceptions.ClientError as e:
                error_code = int(e.response['Error']['Code'])
            
                if error_code != 404:
                    raise

                is_exists = False

        logger.debug('is_exists: %s (cache_fp: %s).' % (is_exists, cache_fp))

        return is_exists

    def resolve(self, ident):
        try:
            key = urllib.unquote(ident)

            cache_info_fp = self._get_key_from_file(key, '.info')
            cache_fp = self._get_key_from_file(key, '.cache')

            logger.debug('resolve (ident: %s, key: %s, cache_fp: %s).' % (ident, key, cache_fp))

            if (os.path.exists(cache_info_fp)):
                with io.open(cache_info_fp, 'rb') as f:
                    # pickle でオブジェクトをロードします。
                    cache_info = pickle.loads(zlib.decompress(f.read()))

                format = FORMATS_BY_MEDIA_TYPE[cache_info['content_type']]
            else:
                obj = self._bucket.Object(key)
                obj.load()

                format = FORMATS_BY_MEDIA_TYPE[obj.content_type]

                with io.open(cache_info_fp, 'wb') as f:
                    cache_info = {
                        'content_length': obj.content_length,
                        'content_type': obj.content_type
                    }

                    f.write(zlib.compress(pickle.dumps(cache_info, pickle.HIGHEST_PROTOCOL)))

                obj.download_file(cache_fp)
        except botocore.exceptions.ClientError as e:
            error_code = int(e.response['Error']['Code'])
        
            if error_code != 404:
                raise

            raise ResolverException(404, 'Source image not found for identifier: %s.' % (ident,))

        return (cache_fp, format)

    def _createdir(self):
        if not os.path.exists(self._cache_dir):
            try:
                os.makedirs(self._cache_dir, 0o700)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise EnvironmentError("キャッシュディレクトリ (%s) が生成できませんでした。" % self._cache_dir)

    def _get_key_from_file(self, key, suffix):
        # キーのハッシュからファイルパスを生成します。
        return os.path.join(self._cache_dir, ''.join([
            hashlib.md5(key.encode('utf-8', 'strict')).hexdigest(),
            suffix
        ]))
