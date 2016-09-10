# docker-loris
[Loris IIIF Image Server](https://github.com/loris-imageserver/loris) の docker コンテナです。

Amazon S3 の API を利用する Resolver を同梱しているため、
SimpleHTTPResolver などで対応できないケースでも S3 を利用する事ができます。

## 例

    $ docker run --rm -p 5004:5004 --name loris \
        -v /data/loris2/images:/usr/local/share/images \
        -v /data/loris2/cache/image:/var/cache/loris2 \
        cosmicvelocity/loris:2.0.1-1

## ドキュメント

### 使い方

#### コンテナのビルド

    git clone https://github.com/cosmicvelocity/docker-loris.git
    cd docker-loris
    git checkout 2.0.1-1
    cd 2.0.1-1
    docker build -t cosmicvelocity/loris:2.0.1-1 .

#### コンテナ上の各フォルダ

- /usr/local/share/images - 画像を参照します。
- /var/cache/loris2 - Image API で加工された画像のキャッシュを保存します。

#### コンテナの実行

    $ docker run --rm -p 5004:5004 --name loris \
        -v /data/loris2/images:/usr/local/share/images \
        -v /data/loris2/cache/image:/var/cache/loris2 \
        cosmicvelocity/loris:2.0.1-1

### Amazon S3 を使う場合

Amazon S3 を使う Resolver が組み込まれています。
利用する場合はバージョンフォルダ中の conf/loris2.conf を変更してビルドするか、
ビルドしたイメージを利用する Dockerfile を作成してカスタマイズした loris2.conf を組み込みます。
    
組み込む場合は loris2.conf の [resolver] エントリを下記のように変更します。
    
    [resolver]
    impl = 's3resolver.S3Resolver'
    region_name = '【リージョン名】'
    aws_access_key_id = '【アクセスキーID】'
    aws_secret_access_key = '【シークレットアクセスキー】'
    bucket_name = '【バケット名】'
    cache_dir = '【S3 から取得した画像のキャッシュディレクトリのパス】'
    
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
        -v /data/loris2/cache/image:/var/cache/loris2 \
        -v /data/loris2/cache/s3:/var/cache/loris2-s3 \
        cosmicvelocity/loris:2.0.1-1
