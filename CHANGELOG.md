# [1.9.0](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.8.0...v1.9.0) (2025-05-14)


### Features

* conexión con InfluxDB ([f66682a](https://github.com/adriantoral/ingenieria-datos-viabi/commit/f66682a39042b0713d7f1c5fdedeef77f0e7f66b))
* frames del visor ([fc9ce92](https://github.com/adriantoral/ingenieria-datos-viabi/commit/fc9ce92cfbd9f319157bdfee5d6e08c9f922b888))
* visor con influxDB ([8a4572f](https://github.com/adriantoral/ingenieria-datos-viabi/commit/8a4572faaaa7592b1f9ea1b3502bd448612a7888))
* visor de intrusión estático ([a38c412](https://github.com/adriantoral/ingenieria-datos-viabi/commit/a38c4124e62c8bfd6dcc5bef0b875c3e984954a5))
* visor en tiempo real ([d72d898](https://github.com/adriantoral/ingenieria-datos-viabi/commit/d72d8988696c5a096f10dd038a9bcb3ed6faee73))

# [1.8.0](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.7.0...v1.8.0) (2025-05-04)


### Features

* Cambios del visor de doble camara ([7475c0a](https://github.com/adriantoral/ingenieria-datos-viabi/commit/7475c0a4454feec90d2b94be623f5377a02c0446))

# [1.7.0](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.6.0...v1.7.0) (2025-04-02)


### Features

* agrega autoescalado completo de MinIO, InfluxDB, RabbitMQ, consumer y persistencia de token ([d99b31f](https://github.com/adriantoral/ingenieria-datos-viabi/commit/d99b31f5bb379324d8a7b5b119695626bd3c2b90))

# [1.6.0](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.5.1...v1.6.0) (2025-04-02)


### Features

* + de 2 minutos guardados ([ad380f1](https://github.com/adriantoral/ingenieria-datos-viabi/commit/ad380f17d503903856c16ee56e914f279e3045ad))
* Buffer implementado ([260ad0a](https://github.com/adriantoral/ingenieria-datos-viabi/commit/260ad0aeffe75952bfa14496a25ddeaac155edb5))
* Cambio de tiempo va mas rapido ([db80d24](https://github.com/adriantoral/ingenieria-datos-viabi/commit/db80d24811e50b876482ff2b0d9d75d854da4788))
* cambios pequeños ([a92ac74](https://github.com/adriantoral/ingenieria-datos-viabi/commit/a92ac749199ddd007ca741c664f2aad4639fcab9))
* Hora en la camaras ([145f92f](https://github.com/adriantoral/ingenieria-datos-viabi/commit/145f92f087c1e1b8cc115674689fd4930ad2551c))
* Se muestra el video ([44104d6](https://github.com/adriantoral/ingenieria-datos-viabi/commit/44104d63bf483c9cad0428562b74e113fd06fb67))
* Visor a Develop ([1a418c1](https://github.com/adriantoral/ingenieria-datos-viabi/commit/1a418c10614cce632b875354557469c6e9110f88))

## [1.5.1](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.5.0...v1.5.1) (2025-03-26)


### Bug Fixes

* arregla un error en las variables de entorno ([0c3f7e2](https://github.com/adriantoral/ingenieria-datos-viabi/commit/0c3f7e254071c41325a6cf75299b97d50a69d8ee))

# [1.5.0](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.4.0...v1.5.0) (2025-03-26)


### Features

* actualiza el yaml del consumer de images ([2a53726](https://github.com/adriantoral/ingenieria-datos-viabi/commit/2a53726806eaae1660799baa59d01698f06ed976))
* actualiza el yaml del consumer de metadata ([de4f243](https://github.com/adriantoral/ingenieria-datos-viabi/commit/de4f243d080b70153730d0d452be594cb7ee5534))
* divide consumer en dos partes minio e influx ([9e62934](https://github.com/adriantoral/ingenieria-datos-viabi/commit/9e62934d72843504eecb44edf83befdfe16f1040))

# [1.4.0](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.3.0...v1.4.0) (2025-03-26)


### Features

* separa el envio de metadatos y video en dos colas distintas ([c89bd51](https://github.com/adriantoral/ingenieria-datos-viabi/commit/c89bd51b7d1cf07290231e3bd9354d33c2a7ed27))

# [1.3.0](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.2.4...v1.3.0) (2025-03-10)


### Features

* agrega producer en local sin kubernetes ([9404c91](https://github.com/adriantoral/ingenieria-datos-viabi/commit/9404c91b0490dd65013850d169975840198a8233))

## [1.2.4](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.2.3...v1.2.4) (2025-03-05)


### Bug Fixes

* actualiza el consumer para enviar ack manual ([a8db6e9](https://github.com/adriantoral/ingenieria-datos-viabi/commit/a8db6e926f586ea1ba3e25484356b9090c7552fc))

## [1.2.3](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.2.2...v1.2.3) (2025-03-05)


### Bug Fixes

* actualiza las credenciales de acceso ([ad94932](https://github.com/adriantoral/ingenieria-datos-viabi/commit/ad94932d035e94baef203146e9a0f1fc5abfda40))

## [1.2.2](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.2.1...v1.2.2) (2025-02-26)


### Bug Fixes

* elimina los servicios obsoletos ([ddb8831](https://github.com/adriantoral/ingenieria-datos-viabi/commit/ddb88311dbb3db41a4e5c80cb0cb4ac26f4ed199))

## [1.2.1](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.2.0...v1.2.1) (2025-02-26)


### Bug Fixes

* actualiza los deployments de influxdb, minio, rabbitmq y el consumer ([12dfe7f](https://github.com/adriantoral/ingenieria-datos-viabi/commit/12dfe7ff659718432cd1c38fae0103360a0119b9))

# [1.2.0](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.1.0...v1.2.0) (2025-02-26)


### Features

* add producer and cosumer ([a5c80ba](https://github.com/adriantoral/ingenieria-datos-viabi/commit/a5c80bac8abbc1ff7616595fba6021e31747c445))

# [1.1.0](https://github.com/adriantoral/ingenieria-datos-viabi/compare/v1.0.0...v1.1.0) (2025-02-26)


### Features

* add yaml for influxdb and minio deployments ([316a2cd](https://github.com/adriantoral/ingenieria-datos-viabi/commit/316a2cd40330bd572fda5550f8004b1b1fdf2ae4))
* add yaml for influxdb and minio deployments ([66f98db](https://github.com/adriantoral/ingenieria-datos-viabi/commit/66f98db3bae60c18f1600ee9b0d1b66d706ad6a7))

# 1.0.0 (2025-02-26)


### Features

* actualiza rabbitmq para usar modo cluster ([2ea9a4d](https://github.com/adriantoral/ingenieria-datos-viabi/commit/2ea9a4df6a3d6c0b463442bae2529d6733b0ab51))
* add semantic release for automatic version control ([cfbeb57](https://github.com/adriantoral/ingenieria-datos-viabi/commit/cfbeb57e4efb417c1e20679d7d708a8144dbbb3f))
* agrega la estructura inicial de kubernetes ([c5a5932](https://github.com/adriantoral/ingenieria-datos-viabi/commit/c5a5932bd7049c83e557d9e032f01be28dd7bd00))
* agrega rabbitmq, un consumidor y un productor basico ([fb9bea1](https://github.com/adriantoral/ingenieria-datos-viabi/commit/fb9bea101bdfa53208e0162588834b6ea93f13a1))
* elimina kafka para transicionar a rabbitMQ ([47766bd](https://github.com/adriantoral/ingenieria-datos-viabi/commit/47766bd3b5f12d0ab85077e1eeb664ed0be41117))
