# 技術選定

## data management / tracking

- dvc
- mlflow
- sqllineage

## GRPC

### framework

- [bali](https://github.com/bali-framework/bali): fastapiとGRPCを統合
- [sonora](https://github.com/public/sonora): ASGIとGRPCを統合
- [Hypercorn](https://github.com/pgjones/hypercorn): 高速HTTP/2 ASGIサーバ。uvicornはHTTP/1.1の対応？

### Converter

- [openapi-generator](https://github.com/OpenAPITools/openapi-generator/pull/3818): java製。プロダクトに組み込む場合は、dockerなどを用意。
- [gnostic](https://github.com/google/gnostic): go製。googleが開発。openapi to grpcのみに特化。star 1.3k
- [openapi2proto](https://github.com/nytimes/openapi2proto): go製。 star: 0.8k


## ML Format

- ONNX（Open Neural Network Exchange）:機械学習のモデルを表現するための代表的なフォーマット。全てのライブラリがこのフォーマットに準拠しているわけではない。


## ML Serving

学習したモデルを本番環境にAPIとして公開する

- TensorFlow Serving
- Multi Model Server
- TorchServe

