; Скрипт Inno Setup для создания установщика ChatList
; Версия автоматически обновляется из version.py через generate_installer.py

#define AppName "ChatList"
#define AppPublisher "ChatList Team"
#define AppURL "https://github.com/VladimirBaliev/ChatList"
#define AppExeName "ChatList-v1.0.0.exe"
#define AppVersion "1.0.0"
#define AppVersion "1.0.0"

[Setup]
; Основные настройки
AppId={{A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer
OutputBaseFilename=ChatList-Setup-v{#AppVersion}
SetupIconFile=app.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; В режиме onedir устанавливаем всю папку с exe и зависимостями
Source: "dist\ChatList-v{#AppVersion}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "app.ico"; DestDir: "{app}"; Flags: ignoreversion
; Добавьте другие файлы, если необходимо

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\app.ico"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\app.ico"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\app.ico"; WorkingDir: "{app}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent; WorkingDir: "{app}"

[UninstallDelete]
; Удаление файлов и папок при деинсталляции
Type: filesandordirs; Name: "{app}\*.*"
Type: dirifempty; Name: "{app}"

[Code]
// Секция Uninstall - дополнительные действия при удалении
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  UserDataPath: String;
begin
  case CurUninstallStep of
    usUninstall:
      begin
        // Можно добавить дополнительные действия перед удалением
        // Например, сохранение пользовательских данных
      end;
    usPostUninstall:
      begin
        // Действия после удаления
        // Удаление пользовательских данных (опционально)
        UserDataPath := ExpandConstant('{userappdata}\{#AppName}');
        if DirExists(UserDataPath) then
        begin
          if MsgBox('Удалить пользовательские данные (база данных, настройки)?', 
                    mbConfirmation, MB_YESNO) = IDYES then
          begin
            DelTree(UserDataPath, True, True, True);
          end;
        end;
      end;
  end;
end;

