[Setup]
AppName=Cour Supreme
AppVersion=1.0.0
DefaultDirName={localappdata}\Cour Supreme
DefaultGroupName=Cour supreme
OutputBaseFilename=CourSupremeSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest

[Files]
Source: "dist\courSup.exe"; DestDir: "{app}"; Flags: ignoreversion


[Icons]
Name: "{group}\Cour Supreme"; Filename: "{app}\courSup.exe"; IconFilename: "{app}\drapeau.ico"

[Tasks]
Name: "desktopicon"; Description: "Creer une icone sur le bureau"; GroupDescription: "Options:"; Flags: unchecked

[Run]
Filename: "{app}\courSup.exe"; Description: "Lancer l'application"; Flags: nowait postinstall skipifsilent