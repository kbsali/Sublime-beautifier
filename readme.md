## About
This is mix between the PhpBeautifier (https://github.com/SublimeText/PhpBeautifier) and JsFormat (https://github.com/jdc0589/JsFormat) plugins.
Both were interesting to me, but their key bindings being the same, they were therefore conflicting.

To install it I would recommend using the great Package Control plugin (https://github.com/wbond/sublime_package_control) and add this repository to your personal list of repositories. Maybe one day it will make it to the "official" package control channel! :)

**NOTE** : only tested on Ubuntu

## Installation
Install php-pear and php-cli with your package manager :

 * `apt-get install php-pear php5-cli` (Debian / Ubuntu)

Install php beautifier from pear channel :
 * `sudo pear install --alldeps  channel://pear.php.net/php_beautifier-0.1.15`

Clone or download the files and copy them to your `Packages` folder. You can access it via Preferences -> Browse Packages in sublime text.

## Usage
 * `ctrl + shift + p` and type `Format: Javascript/PHP`
 * `ctrl + alt + f`

## Customize
Various plugin and formatting options can be configured via the settings file, available via `Preferences > Package Settings > Beautifier > Settings - User`.

## TODO
 * Find an alternative to php_beautifier pear install