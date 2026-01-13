; Скрипт Inno Setup для создания установщика ChatList
; Версия автоматически обновляется из version.py через generate_installer.py

#define AppName "ChatList"
#define AppPublisher "ChatList Team"
#define AppURL "https://github.com/VladimirBaliev/ChatList"
#define AppExeName "ChatList-v1.0.0.exe"
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
  LogFilePath: String;
  TempPath: String;
  ResultCode: Integer;
begin
  case CurUninstallStep of
    usUninstall:
      begin
        // Действия перед удалением файлов
        // Закрываем приложение, если оно запущено
        if Exec('taskkill', '/F /IM {#AppExeName}', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
        begin
          // Приложение было закрыто
        end;
      end;
    usPostUninstall:
      begin
        // Действия после удаления файлов программы
        
        // Удаление пользовательских данных (база данных, настройки, логи)
        UserDataPath := ExpandConstant('{userappdata}\{#AppName}');
        if DirExists(UserDataPath) then
        begin
          if MsgBox('Удалить пользовательские данные?' + #13#10 + 
                    '(база данных, настройки, логи будут удалены)', 
                    mbConfirmation, MB_YESNO) = IDYES then
          begin
            // Удаляем пользовательские данные
            if DelTree(UserDataPath, True, True, True) then
            begin
              // Успешно удалено
            end;
          end;
        end;
        
        // Удаление лог файла из временной директории (если есть)
        LogFilePath := ExpandConstant('{localappdata}\Temp\chatlist.log');
        if FileExists(LogFilePath) then
        begin
          DeleteFile(LogFilePath);
        end;
        
        // Удаление лог файла из директории приложения (если остался)
        LogFilePath := ExpandConstant('{app}\chatlist.log');
        if FileExists(LogFilePath) then
        begin
          DeleteFile(LogFilePath);
        end;
        
        // Удаление временных файлов (если есть)
        TempPath := ExpandConstant('{tmp}\{#AppName}');
        if DirExists(TempPath) then
        begin
          DelTree(TempPath, True, True, True);
        end;
        
        // Удаление пустых директорий
        if DirExists(ExpandConstant('{app}')) then
        begin
          RemoveDir(ExpandConstant('{app}'));
        end;
      end;
  end;
end;

// Функция для проверки, запущено ли приложение
function InitializeUninstall(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // Проверяем, запущено ли приложение
  if Exec('tasklist', '/FI "IMAGENAME eq {#AppExeName}" /FO CSV', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
    begin
      // Приложение запущено, предлагаем закрыть
      if MsgBox('Приложение {#AppName} запущено.' + #13#10 + 
                'Необходимо закрыть его перед удалением.' + #13#10#13#10 +
                'Закрыть приложение сейчас?', 
                mbConfirmation, MB_YESNO) = IDYES then
      begin
        // Закрываем приложение
        Exec('taskkill', '/F /IM {#AppExeName}', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
        Sleep(1000); // Даём время на закрытие
      end
      else
      begin
        // Пользователь отказался закрывать приложение
        MsgBox('Удаление отменено. Закройте приложение вручную и попробуйте снова.', 
               mbError, MB_OK);
        Result := False;
      end;
    end;
  end;
end;

