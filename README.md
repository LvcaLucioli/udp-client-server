
# Traccia 2: 


Architettura client-server UDP per trasferimento file. Il software permette connessione client-server senza autenticazione, la visualizzazione (da parte del client) dei file disponibili sul server e il download e l'upload di file.

# Esecuzione

Entrambi gli script ricevono come parametro un intero che rappresenta la porta sulla quale opera il server.
Per l'esecuzione delle due componenti è sufficiente aprire due finestre di terminale e lanciare i due eseguibili con l'opportuno parametro.
 
Avvio del server:
```
PS C:\Users\Admin\path\to\server> .\server.exe 10000
```
Avvio del client allo stesso modo:
```
PS C:\Users\Admin\path\to\client> .\client.exe 10000
```
# Comandi
* **help**: mosta la lista dei comandi disponibili
* **get <filename>**: download del file remoto dal server
* **put <filename>**: upload del file locale sul server
* **list**: mostra la lista dei file presenti nel server 
* **quit**:

