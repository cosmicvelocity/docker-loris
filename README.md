# docker-loris
[Loris IIIF Image Server](https://github.com/loris-imageserver/loris) の docker イメージです。

本家のイメージと比較して、下記の特徴があります。

- Alpine Linux をベースにしているため、イメージサイズが小さいです。
- Amazon S3 API を利用する Resolver を同梱しています。
- 商用利用を想定して構成しているため、Kakadu のプロダクトは除いてあります。

## サポートされているタグ

- latest - loris development branch ([Dockerfile](https://github.com/cosmicvelocity/docker-loris/raw/master/Dockerfile))
- 2.1.0 - loris 2.1.0 ([Dockerfile](https://github.com/cosmicvelocity/docker-loris/raw/2.1.0/Dockerfile))

## イメージの使い方

    $ docker run --rm -p 5004:5004 cosmicvelocity/loris:latest

起動後、ブラウザで下記にアクセスします。

    http://[<Host or Container IP>]:5004/test.png/full/full/0/default.jpg

### コンテナ上の各ファイル・フォルダ
- **/etc/loris2/loris2.conf**  
    Loris が参照する設定ファイルのパス。

- **/var/cache/loris2**  
    Loris が IIIF Image API で加工された画像などのキャッシュを保存するフォルダ。

下記は設定ファイルの設定によります。

- **/usr/local/share/images**  
    SimpleFSResolver を利用する場合、参照する画像ファイルの配置フォルダ。

- **/usr/local/share/images/loris**  
    SimpleHTTPResolver, TemplateHTTPResolver, S3Resolver を利用する場合、リモートの画像ファイルのキャッシュを保存するフォルダ。

参照画像ファイルの配置フォルダを指定する際は下記のようになります。

    $ docker run --rm -p 5004:5004 -v /data/loris2/images:/usr/local/share/images cosmicvelocity/loris:latest

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
本番運用するには機能が不足しているので、その点ご注意ください。
    
#### 設定例

    [resolver]
    impl = 's3resolver.S3Resolver'
    region_name = 'ap-northeast-1'
    aws_access_key_id = '....'
    aws_secret_access_key = '....'
    bucket_name = 'sample'
    cache_dir = '/usr/local/share/images/loris'

#### コンテナの起動

    $ docker run --rm -p 5004:5004 -v /data/images:/usr/local/share/images -v /data/loris2/conf/loris2.conf:/etc/loris2/loris2.conf -v /data/loris2/cache/image:/var/cache/loris2 -v /data/loris2/cache/s3:/usr/local/share/images/loris cosmicvelocity/loris:latest

## ライセンス
このイメージに含まれるソフトウェアのライセンス情報は下記を参照ください。

- [loris](https://github.com/loris-imageserver/loris/blob/development/LICENSE-Loris.txt)
- [openjpeg](https://github.com/uclouvain/openjpeg/blob/master/LICENSE)
