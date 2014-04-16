=======
rtshell
=======

イントロダクション
==================

rtcshell は、ネームサーバ上に登録されているRTコンポーネントをシェルから
管理することができるツールです。コンポーネントを
activate/deactivate/resetしたり、ポートの接続を行うことができます。RTシ
ステムを管理することもできます。

このツールは、リソースの少ないシステム、GUIが利用できない環境(特に、コン
ポーネントを管理する他のPCとネットワークがつながっていない環境等)、ある
いはRTSystemEditorがどうしても利用できない場合等に有効です。コマンドライ
ンの利用に精通している人にとっては特に便利なツールです。

このソフトウエアはNEDO (独立行政法人 新エネルギー・産業技術総合開発機構)
の次世代ロボット知能化技術開発プロジェクトの支援により、独立行政法人産業
技術総合研究所によって開発されています。管理番号H23PRO-1214.

This software is licensed under the Eclipse Public License -v 1.0 (EPL).
See LICENSE.txt.


必要条件
========

- rtctree 3.0以上が必要となります.

- rtsprofile-2.0 が必要となります。

- Python 2.5以下では存在しない機能を使うので、Python 2.6以上が必要となり
  ます。

- rtprint、rtinjectおよびrtlogはOpenRTM-Python-1.0.0以上が必要となります。

- Ubuntu 9.04を使っていたら、手動でPython 2.6をインストールすることが必
  要となります。Ubuntu 9.04以上をおすすめします。


インストール
============

インストールはいくつかの方法が利用可能です。

  1.リポジトリまたはソースアーカイブからダウンロード後、適当なディレクト
  リで解凍し、そこでコマンドを実行する。

  2.リポジトリまたはソースアーカイブからダウンロード後、適当なディレクト
  リで解凍し、インストールする。

    a) ソースを展開する::

        $ cd /home/blurgle/src/
        $ tar -xvzf rtshell-3.0.0.tar.gz

    b) setup.pyを実行する::

        $ python setup.py install

    c) 必要に応じて、環境変数を設定します。これはデフォルトで設定されて
    いますが、設定されていない場合は自分で設定する必要があります。
    Windows上では、Python の site-packages ディレクトリが ``PYTHONPATH``
    環境変数に、Pythonスクリプトのディレクトリが PATH 環境変数に設定され
    ていることを確認してください。通常、これらは
    ``C:\Python26\Lib\site-packages\`` と ``C:\Python26\Scripts\``
    です（Pythonが``C:\Python26\``にインストールされた場合）。

  3. Windows ではインストーラの使用を推奨します。``setup.py`` を利用すれ
  ば結果より容易に設定することができます。ただし、環境によってはさらに環
  境変数の設定が必要な場合があります。

  4. Windows　ではない場合、シェルスクリプトをインストールする必要です。
  ``${prefix}/share/rtshell/shell_support``（${prefix}はrtcshellをインス
  トールされたディレクトリです。）というファイルを``source``コマンドに
  よってロードしてください（例はrtshellが``/usr/local``にインストールさ
  れた場合）::

    source /usr/local/share/rtshell/shell_support

  いつも新しいシェルを実効する時に以上のコマンドを実効することは必要な
  いように以下の行を``.bashrc``などのファイルに追加してください
  （rtshellが``/usr/local``にインストールsされた場合）::

    source /usr/local/share/rtshell/shell_support


リポジトリ
==========

最新版のソースはgithubでGitのリポジトリにあります（URL:
``http://github.com/gbiggs/rtshell`` ）。「Download
source」をクリックしてダウンロードをすることができます。「git
clone」を使うこともできます。パッチを送りたがったら、この方法がおすすめ
します::

  $ git clone git://github.com/gbiggs/rtshell.git


ドキュメント
============

ドキュメントはマンページとして提供します（Windowsの場合はHTMLに提供しま
す）。``${prefix}/share/man``にインストールされます。このパスを
``$MANPATH``という環境変数に追加する必要です。例えば、rtshellは
``/usr/local``にインストールされた場合、以下の行を``.bashrc``に追加して
ください::

  export MANPATH=/usr/local/share/man:${MANPATH}


テストの実効
============

コマンドのテストはソースダイレクトリから実効することができます::

~/src/rtshell $ ./test/test_cmds.py ~/share/OpenRTM-aist/examples/rtcs/

変数はRTCのモジュールを持つダイレクトリです。``Motor``、``Controller``
および``Sensor``のモジュールが必要です。

一つのコマンドのテストだけを実効するの場合、そのテストの名を変数に追加
してください::

$ ./test/test_cmds.py ~/share/OpenRTM-aist/examples/rtcs/ rtactTests


Changelog
=========

4.0
---

- コネクタプロパティの保存と復活を直した。
- Windowsで色字の出力を消した。
- OpenRTMの新しいデー多型表地方に従う。
- URLに合わせるために全部のos.sepを'/'に変更しました。
- 新しいコマンド：rtvlog(コンポーネントのログメッセージの表示)
- rtact/rtdeact/rtreset：一つのコマンドで複数のコンポーネントを変更
  できるようにしました。
- rtcomp: 分散コンポーネントの管理を可能にしました。
- rtcon：三つ以上のポートを一つのコネクションで接続できるようにしました。
- rtdis：三つ以上のポートを一つのコネクションを消せるようにしました。
- rtlog：simpklログフォーマットに最後のレコードのポインタを追加しました。
- rtmgr：「corbaloc::」アドレスによって直接マネージャにつながれるように
  しました。
- rtmgr：コマンドを複数回に使えるようにしました。
- rtmgr：コマンドを指定された順番に実行するようにしました。

3.0.1
-----

- Fixed #13: Error with unknown ports when saving systems using rtcryo.
- Fixed #14/#15: Properly handle data types that include versions and IDL
  paths in rtprint.
- Fixed #16: Handle component instance names that include parantheses.


3.0
---

- rtcshellとrtsshellをマージしました。
- コマンドのドキュメントを作成しました。
- 新しいコマンド：rtdoc(コンポーネントのドキュメントを表示するー松坂様より)
- 新しいコマンド：rtexit（コンポーネントを終了する）
- 新しいコマンド：rtlog（ログの記録と再生を行う）
- 新しいコマンド：rtcheck（起動中のRTシステムと、保存されたRTSProfileとを比較する）
- 新しいコマンド：rtcomp（コンポジットコンポーネントを作る）
- 新しいコマンド：rtstodot（起動中のRTシステムをグラフで表示するー松坂様より）
- 新しいコマンド：rtvis（起動中のRTシステムをグラフで表示する）
- rtconfのセット名、パラメータ名及び値の変更の際にbash補間機能を使えるように対応しました。
- シェルサポートファイルをマージしました。
- rtconfのコマンドラインを作り直しました。
- ゾンビオブジェクトに対応しました。
- rtlsでゾンビを表示するようにしました。
- rtdelで全てのゾンビを消せるようにしました。
- rtctreeでの木構造を早く作成するために、パスフィルターをサポートしました。
- rtcat：一個のポートの情報だけを表示するオプションを追加しました。
- rtcat：--llを-llに変更しました。
- rtcat：コンポジットコンポーネントの情報を表示します。
- rtcryo：RtsProfileを標準出力に出します。
- rtdis：IDによってコネクションを削除するオプションを追加しました。
- rtinject/rtprint：ユーザ定義のデータ型に対応しました。
- rtprint：データを一回もらって終了するオプションを追加しました。
- rtprint：ユーザ定義のデータフォーマッタを対応しました。
- rtprint：Pythonの生データを表示するオプションを追加しました。
- rtinject：標準入力からPythonの生データを使えるようにしました。
- rtresurrect：既に存在する接続を再作成しないようにしました。
- rtteardown：コネクタIDが合わない場合エラーを出して終了します。
- rtresurrect/rtstart/rtstop/rtteardown：標準入力で入力を受けとります。
- rtsshellからのコマンドをライブラリとして使用できるようにしました。
- テストを追加しました。


rtcshell-2.0
------------

- Windows対応のための調整。
- 親ディレクトリを示すパスの扱い方を修正しました。
- 新しいコマンド：rtdel
- 新しいコマンド：rtinject
- 新しいコマンド：rtprint
- rtcat：未知の接続の数を表示します。
- リファクタリング:全てのコマンドをPythonのスクリプトからも簡単に使えるようにしました。
- シェル補完機能の追加（鈴木圭介氏より提供）
- rtcwdをcsh系のシェルで使用できるようにしました。
- rtcat：rtctreeから取得できるようになった実行コンテキストに関する新しい情報を表示します。
- rtls：lsと一致するように再帰オプションを-rから-Rにの変更しました。
- rtls：未知のオブジェクトを死んだファイルとして表示します。

rtsshell-2.0
------------

- シェル補完機能の追加（鈴木圭介氏より提供）
- プランニングの機能の追加

