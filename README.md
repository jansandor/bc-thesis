# Sportdiag

https://theses.cz/id/6nrcu2/

## Lokální spuštění aplikace

Tato sekce popisuje lokální spuštění aplikace na OS Ubuntu 20.04 LTS (Desktop). Předpokládá se, že je na systému
nainstalovaný Python ve verzi 3.8.

Jako první krok doporučuji vytvořit virtuální prostředí, ale není to nezbytně
nutné. Vytvořit a používat virtuální prostředí lze prostřednictvím standardního Python
modulu [venv](https://docs.python.org/3.8/tutorial/venv.html), který je součásti instalace jazyka Python nebo
s pomocí nástroje [virtualenv](https://virtualenv.pypa.io/en/latest/index.html).

1. Zkopírujte obsah adresáře *src* do libovolné složky a otevřete ji v příkazové řádce.
2. Aktivujte virtualní prostředí (pokud jste se rozhodli jej vytvořit).
3. Nainstalujte závislosti společné pro všechna prostředí zadáním příkazu `pip install -r requirements/base.txt`.
4. Nainstalujte zbývající závislosti zadáním příkazu `pip install -r requirements/dev.txt`.
5. Aplikujte migrace databáze příkazem `python manage.py migrate --settings=bp.settings.local`.
    1. V rámci migrací je vytvořen účet super uživatele *admin@sportdiag.cz*. Heslo je k dispozici v souboru *.env* pod
       klíčem DJANGO_SUPERUSER_PASSWORD. Pod tímto účtem lze přistupovat na adresu *localhost:8000/admin*.
    2. Při migraci jsou v databázi vytvořeni demo uživatelé a v aktuálním adresáři by se měly objevit soubory
       *approved_fake_psychologists_raw_passwords.txt*, *fake_researchers_raw_passwords.txt* a
       *demo_clients_raw_passwords.txt*. V těch naleznete přístupové údaje k jednotlivým účtům. Klientů i psychologů je
       vytvořeno
       více, ale všichni klienti s přístupy v souboru *demo_clients_raw_passwords.txt* jsou spárováni s testovacím účtem
       psychologa *psycholog@example.com*. V souboru *approved_fake_psychologists_raw_passwords.txt* jsou přístupy pouze
       k účtům schválených výzkumníkem-administrátorem (jsou aktivní a lze se k nim přihlásit).
6. Spusťte lokální server příkazem `python manage.py runserver --settings=bp.settings.local`.
7. Aplikace je nyní dostupná v prohlížeči na adrese *localhost:8000*.

## Nasazení aplikace na server

Tato sekce popisuje nasazení aplikace na server (virtuální stroj) s OS Ubuntu Server 20.04.3 LTS a hardwarovou
konfigurací: 2 jádra CPU, 2 GB RAM a 20 GB diskového prostoru. O zajištění serveru pro účely testování aplikace jsem
požádal správce sítě PřF UPOL.

Předpokládám, že čtenáři tohoto dokumentu nečiní potíže připojit se na vzdálený server pomocí *ssh* a za výchozí situaci
považuji, že je čtenář k serveru připojený a má případně k dispozici otevřenou další příkazovou řádku na svém lokálním
počítači.

1. Prvním krokem pro úspěšné nasazení je mít na serveru nainstalovaný Docker. Toho lze docílit
   podle [oficiálních instrukcí](https://docs.docker.com/engine/install/ubuntu/).
2. Když máme Docker nainstalovaný, je potřeba dostat obsah adresáře *src* na server. V příkazové řádce lokálního
   počítače otevřeme adresář, ve kterém se nachází adresář *src*.
3. Použijeme nástroj *scp* ke zkopírování obsahu adresáře z lokálního počítače na server např.
   takto: `scp -r /local/directory remote_username@10.10.0.2:/remote/directory`
   viz. [zde](https://linuxize.com/post/how-to-use-scp-command-to-securely-transfer-files/#copy-a-local-file-to-a-remote-system-with-the-scp-command).
   V mém konkrétním případě měl příkaz podobu `scp -r ./src sandja00@158.194.92.116:~/`. Po zadání příkazu je nutné
   zadat heslo pro připojení k serveru.
4. Po předchozím kroku bychom již měli na serveru mít adresář *src* (nebo jiný, pokud jsme zvolili jiný název) včetně
   jeho obsahu. Nyní se stačí navigovat dovnitř adresáře a zadat
   příkaz `docker-compose -f docker-compose.prod.yml up -d`. Pokud se jedná o první provedení příkazu, může chvíli
   trvat, než se kontejnery vytvoří.
5. Příkazem `docker ps` můžeme zkontrolovat, že kontejnery běží. Měly by být tři, v mém příapadě s názvy "
   src_nginx_1", "src_sportdiag_web_app_1" a "src_db_1". Názvy se však mohou drobně lišit.
6. Aplikace je nyní dostupná na adrese serveru. V mém případě na IP adrese 158.194.92.116 (protokol HTTP,
   je tedy třeba explicitně zadat http://158.194.92.116/).
