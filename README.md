# Blockchain en Python
Este es un proyecto de implementación básica de una cadena de bloques (blockchain) en Python. La implementación utiliza Flask para la comunicación entre los nodos de una red local y Postman para capturar las respuestas del servicio web a las solicitudes. 

## Requisitos previos
* Python 3.10 en adelante instalado en su sistema.
* Flask 2.2.2.
* requests 2.31.0.
* Postman o un navegador web para leer las respuestas del servidor y enviar solicitudes.

## Instalación
Clone este repositorio en su máquina local: `git clone https://github.com/SebasVM123/Blockchain.git`  
Instale las dependencias del proyecto: `pip install -r requirements.txt`

## Funcionamiento
* **blockchain.py**: En este módulo se encuentra la lógica central de la blockchain. Aquí se define la estructura de los bloques, las transacciones, las carteras (wallets) y las funciones para agregar bloques, realizar pruebas de trabajo, validar la cadena, generar y sincronizar carteras, y realizar transacciones entre wallets. Se implementa la lógica para el protocolo de consenso, donde los nodos en la red verifican y aceptan la cadena de bloques más larga como la válida.
También se incluyen métodos para difundir transacciones a todos los nodos de la red y mantener actualizados los registros de saldos de las carteras.
* **routes.py**: Este módulo proporciona las rutas y controladores para la interacción con la blockchain a través de solicitudes HTTP. Se utilizan decoradores de Flask para definir las rutas y métodos HTTP correspondientes para cada funcionalidad de la blockchain, como minar bloques (/mine_block), agregar transacciones (/add_transaction), obtener la cadena completa (/get_chain), verificar validez (/is_valid), conectar nodos (/connect_node), enviar monedas (/send_coins), entre otros.
* **path.py**: eso inicia la aplicación Flask en un servidor local en el puerto 5000 y accesible por todas las interfaces de red del sistema.

## Características
* Creación de bloques y adición de transacciones.
* Generación y sincronización de carteras (wallets) para cada usuario/nodo en la red.
* Minado de bloques mediante pruebas de trabajo para asegurar la integridad de la cadena.
* Verificación de la validez de la cadena y reemplazo por la cadena más larga en la red.
* Conexión y sincronización de nodos para mantener una cadena de bloques unificada.
* Envío seguro de monedas entre carteras mediante transacciones verificadas y difundidas en la red.
* Obtención de información como la cadena completa, el saldo de una cartera y la generación de nuevas carteras.

## Ejecución
Inicie el servidor ejecutando el archivo *path.py* desde su IDE o bien `python path.py` desde la consola de comandos.
*Nota: asegúrese de haber instalado las dependencias*

## Funcionalidades
* /mine_block (get): minará un bloque y regresará un mensaje que contiene información del bloque.
* /get_chain (get): retorna la cadena actual del nodo.
* /is_valid (get): determina si una cadena dada es válida o no si los hashes anteriores de cada bloque son consistentes con los hashes del bloque anterior, también valida que los proof sean válidos.
* /add_transaction (post): recibe un archivo json en el cuerpo de la solicitud con el siguiente formato:
```
{
    "sender": "", "receiver": "", "amount": 10
}
```
  Y retorna un mensaje de exito o de fracaso. Se debe proporcionar en sender y en receiver un nombre.
* /connect_node (post): recibe un archivo json en el cuerpo de la solicitud con el siguiente formato:
```
{
    "nodes": ["ip:port", "ip:port", "ip:port"]
}
```
  Donde *nodes* es una lista de nodos a la que queremos conectar el nodo local.
* /replace_chain (get): busca entre toda la red de nodos cadenas más largas y, de ser así, las reemplaza. Retorna un mensaje dependiendo si la cadena fue reemplazada o no.
* /get_wallets (get): retorna las wallets de la blockchain.
* /generate_wallet (get): crea una wallet con saldo 100 y retorna su dirección.
* /get_balance/\<address> (get): retorna el balance de una wallet pasándole en la ruta la dirección de la wallet.
* /send_coins (post): recibe en el cuerpo de la solicitud un json con el siguiente formato:
```
{
    "receiver": "", "amount": 10
}
```
  Y retorna un mensaje de la transacción. Se debe proporcionar en receiver la dirección de una wallet válida.

## Implementación.
Para la implementación de este blockchain hay dos cosas a considerar:
* Protocolo de consenso: en este proyecto se utilizó el protocolo de consenso de la cadena más larga, que es el mismo que utiliza Bitcoin. Los nodos de la red consideran como la cadena válida a la cadena más larga porque es esta la que contiene mayor cantidad de bloques válidos y la reemplazan por su cadena al detectarla.
* Prueba de trabajo: en una prueba de trabajo, los mineros intentan encontrar un número que combinado con algunos datos del bloque, retorne un hash con un patrón deseado (generalmente los primeros n ceros). Nuestra prueba de trabajo implementa una operación matemática relativamente sencilla que combina el número, llamado new_proof, con el proof del bloque anterior: `hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()`. Se busca un new_proof que elevado al cuadrado y restándole el cuadrado del anterior proof devuelva un hash cuyas primeras cuatro cifras sean 0.

## Créditos
* Gerwin Lambrano
* Juan Pablo Cataño
* Brandon Castaño
* Sebastián Velásquez
### Recursos utilizados:
[1] Papadis, N., & Tassiulas, L. (2020). Blockchain-Based Payment Channel Networks: Challenges and Recent Advances. IEEE Access. DOI: 10.1109/ACCESS.2020.3046020.  
[2] Andreeva, E. (2019, September 21). How decentralized blockchain messenger works. ADAMANT.  
[3] Tapscott, D., Tapscott, A. (2016). Blockchain Revolution. Portfolio, Penguin Publisher Group, a division of Penguin Random House LLC, New York. ISBN: 978-84-234-2655-3.  
[4] Prusty, N. (2017). Building Blockchain Projects. Packt Publishing Ltd. Birmingham, UK. ISBN: 978-1-78712-214-7.  

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulte el archivo LICENSE para obtener más detalles.
