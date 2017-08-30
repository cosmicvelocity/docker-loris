# -*- coding: utf-8 -*-

import boto3
import botocore
import datetime
import hashlib
import io
import json
import logging
import urllib
import urlparse
import os

from loris_exception import LorisException
from loris_exception import ResolverException
from loris.resolver import _AbstractResolver
from loris.img_info import ImageInfo

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

class CacheException(LorisException): pass


"""
S3 から取得したファイルのキャッシュ情報
"""
class CacheInfo:

    def __init__(self, ident = '', src_img_fp = '', obj = None):
        self.ident = ident
        self.created_at = datetime.datetime.utcnow()

        self.src_img_fp = src_img_fp

        if obj is not None:
            self.src_format = FORMATS_BY_MEDIA_TYPE[obj.content_type]
            self.content_type = obj.content_type
            self.content_length = obj.content_length
            self.last_modified = obj.last_modified
        else:
            self.src_format = ''
            self.content_type = ''
            self.content_length = 0
            self.last_modified = None

    @staticmethod
    def load(path):
        if not os.path.exists(path):
            raise CacheException(404)

        cache_info = CacheInfo()

        with open(path, 'r') as f:
            j = json.load(f)

        cache_info.ident = j.get(u'ident')
        cache_info.created_at = datetime.datetime.strptime(j.get(u'created_at'), '%Y-%m-%d %H:%M:%S')

        cache_info.src_img_fp = j.get(u'src_img_fp')
        cache_info.src_format = j.get(u'src_format')
        cache_info.content_type = j.get(u'content_type')
        cache_info.content_length = j.get(u'content_length')

        try:
            cache_info.last_modified = datetime.datetime.strptime(j.get(u'last_modified'), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            cache_info.last_modified = None

        f.close()

        return cache_info

    def save(self, path):
        d = {}

        d['ident'] = self.ident
        d['created_at'] = self.created_at.strftime('%Y-%m-%d %H:%M:%S')

        d['src_img_fp'] = self.src_img_fp
        d['src_format'] = self.src_format

        d['content_type'] = self.content_type
        d['content_length'] = self.content_length

        if self.last_modified is not None:
            d['last_modified'] = self.last_modified.strftime('%Y-%m-%d %H:%M:%S')
        else:
            d['last_modified'] = None

        with open(path, 'w') as f:
            f.write(json.dumps(d, indent = 4))
            f.close()


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

        self._createdirs()

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
        info_fp = self._get_key_from_file(key, '.info')
        is_exists = False

        try:
            cache_info = CacheInfo.load(info_fp)
            is_exists = True

        except CacheException as e:
            try:
                obj = self._bucket.Object(key)
                obj.load()

                is_exists = True
            except botocore.exceptions.ClientError as e:
                error_code = int(e.response['Error']['Code'])

                if error_code != 404:
                    raise

        logger.debug('is_resolvable, is_exists: %s, info_fp: %s' % (is_exists, info_fp))

        return is_exists

    def raise_404_for_ident(self, ident):
        message = 'Source image not found for identifier: %s.' % (ident,)
        logger.warn(message)
        raise ResolverException(404, message)

    def raise_boto_for_ident(self, ident, e):
        error_code = int(e.response['Error']['Code'])

        if error_code != 404:
            raise

        self.raise_404_for_ident(ident)

    def resolve(self, app, ident, base_uri):
        try:
            key = urllib.unquote(ident)
            info_fp = self._get_key_from_file(key, '.info')

            try:
                cache_info = CacheInfo.load(info_fp)
            except CacheException as e:
                src_img_fp = self._get_key_from_file(key, '.cache')

                obj = self._bucket.Object(key)
                obj.load()
                obj.download_file(src_img_fp)

                cache_info = CacheInfo(ident, src_img_fp, obj)
                cache_info.save(info_fp)

        except botocore.exceptions.ClientError as e:
            self.raise_boto_for_ident(ident, e)

        uri = self.fix_base_uri(base_uri)
        source_fp = cache_info.src_img_fp
        format = cache_info.src_format
        extra = self.get_extra_info(ident, source_fp)

        return ImageInfo(app, uri, source_fp, format, extra)

    def _createdirs(self):
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
