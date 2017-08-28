# docker-loris
[Loris IIIF Image Server](https://github.com/loris-imageserver/loris) の docker イメージです。

Amazon S3 の API を利用する Resolver を同梱しているため、
SimpleHTTPResolver などで対応できないケースでも S3 を利用する事ができるほか、
alpine linux をベースにしているので本家のイメージよりもサイズが小さいです。

なお、本家リポジトリには Kakadu のプロダクトが含まれていますが、
商用利用を考慮して本イメージには含まないように構築されています。

## サポートされているタグ

- latest - loris development branch ([Dockerfile](https://github.com/cosmicvelocity/docker-loris/raw/master/Dockerfile))
- 2.1.0 - loris 2.1.0 ([Dockerfile](https://github.com/cosmicvelocity/docker-loris/raw/2.1.0/Dockerfile))

## イメージの使い方

    $ docker run --rm -p 5004:5004 --name loris \
        -v /data/loris2/images:/usr/local/share/images \
        -v /data/loris2/cache/image:/var/cache/loris2 \
        cosmicvelocity/loris:2.1.0

### コンテナ上の各ファイル・フォルダ

- /usr/local/share/images - 画像を参照します。
- /etc/loris2/loris2.conf - 設定ファイルを参照します。
- /var/cache/loris2 - Image API で加工された画像のキャッシュを保存します。

### Amazon S3 を使う場合

Amazon S3 を使う Resolver が組み込まれています。
組み込む場合は loris2.conf の [resolver] エントリを下記のように変更します。
    
    [resolver]
    impl = 's3resolver.S3Resolver'
    region_name = '【リージョン名】'
    aws_access_key_id = '【アクセスキーID】'
    aws_secret_access_key = '【シークレットアクセスキー】'
    bucket_name = '【バケット名】'
    cache_dir = '【S3 から取得した画像のキャッシュディレクトリのパス】'

ただし、試験的な実装になっているので、S3 上のファイルが更新されてもキャッシュが自動更新されない等、
本番運用するには機能が不足しているので、ご注意ください。
    
#### 設定例

    [resolver]
    impl = 's3resolver.S3Resolver'
    region_name = 'ap-northeast-1'
    aws_access_key_id = '....'
    aws_secret_access_key = '....'
    bucket_name = 'sample'
    cache_dir = '/var/cache/loris2-s3'

#### コンテナの起動

    $ docker run --rm -p 5004:5004 --name loris \
        -v /data/images:/usr/local/share/images \
        -v /data/loris2/conf/loris2.conf:/etc/loris2/loris2.conf \
        -v /data/loris2/cache/image:/var/cache/loris2 \
        -v /data/loris2/cache/s3:/var/cache/loris2-s3 \
        cosmicvelocity/loris:2.1.0

## ライセンス
このイメージに含まれるソフトウェアのライセンス情報は下記を参照ください。

- [loris](https://github.com/loris-imageserver/loris/blob/development/LICENSE-Loris.txt)
- [openjpeg](https://github.com/uclouvain/openjpeg/blob/master/LICENSE)
