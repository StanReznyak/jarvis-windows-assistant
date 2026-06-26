#define MyAppName "JARVIS"
#define MyAppVersion "8.4"
#define MyAppPublisher "StanReznyak"
#define MyAppExeName "JARVIS.exe"

[Setup]
AppId={{A03C29AF-6A49-42A2-B862-1C2484C94E45}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=dist_setup
OutputBaseFilename=JARVIS_Setup_v8_4
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=assets\jarvis_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Голосовой помощник JARVIS для Windows
VersionInfoProductName={#MyAppName}

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Дополнительно:"; Flags: unchecked
Name: "autostart"; Description: "Запускать JARVIS вместе с Windows"; GroupDescription: "Дополнительно:"; Flags: unchecked

[Files]
Source: "dist\JARVIS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\JARVIS"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\JARVIS"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\JARVIS"; Filename: "{app}\{#MyAppExeName}"; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустить JARVIS"; Flags: nowait postinstall skipifsilent
