#define MyAppName "xbt"
#define MyAppVersion "1.0"
#define MyAppExeName "main.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
OutputBaseFilename=xbt_installer
SetupIconFile=C:\Users\Harrison Lee\Desktop\x.b.t\logo2.ico
Compression=lzma2/ultra64
SolidCompression=yes

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Files]
Source: "C:\Users\Harrison Lee\Desktop\x.b.t\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Flags: nowait postinstall skipifsilent
