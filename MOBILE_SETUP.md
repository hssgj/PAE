# PAE Mobile — první instalace

PAE Mobile je samostatná Android aplikace. Model, paměť, tools a registry dál běží v Termuxu.

## Jednorázově v Termuxu

```sh
cd ~/PAE
git fetch origin pae-mobile-mvp
git switch pae-mobile-mvp
git pull
chmod +x start-mobile.sh
mkdir -p ~/.termux
grep -q '^allow-external-apps=' ~/.termux/termux.properties 2>/dev/null \
  && sed -i 's/^allow-external-apps=.*/allow-external-apps=true/' ~/.termux/termux.properties \
  || printf '\nallow-external-apps=true\n' >> ~/.termux/termux.properties
termux-reload-settings
./start-mobile.sh
```

Pak v Androidu nainstaluj APK a v **Nastavení → Aplikace → PAE → Oprávnění** povol oprávnění **Run commands in Termux environment**.

Po klepnutí na ikonu PAE aplikace sama zavolá `~/PAE/start-mobile.sh`, počká na lokální rozhraní a otevře chat. Všechna komunikace s motorem probíhá pouze přes `127.0.0.1` uvnitř telefonu.

## Rychlá kontrola bez APK

Po spuštění `./start-mobile.sh` otevři v prohlížeči telefonu:

```text
http://127.0.0.1:8765
```

Pokud se ukáže chat a odpoví PAE, motor i mobilní most fungují. APK pak pouze odstraní nutnost otevírat Termux a zadávat příkaz.
