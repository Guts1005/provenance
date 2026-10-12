; Inno Setup Script for Provenance Industrial Packing Suite
; Generates a single standalone Windows Setup Wizard (Setup_Provenance_v1.0.exe)
; Includes custom wizard page for Video Evidence Clips Storage Directory

#define MyAppName "Provenance"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Provenance Industrial Systems"
#define MyAppURL "https://github.com/provenance-cctv"
#define MyAppExeName "Provenance.exe"

[Setup]
AppId={{E58742DF-29B6-4E87-8BA9-D64D6A12089F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\dist
OutputBaseFilename=Setup_Provenance_v1.0
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "firewallrule"; Description: "Configure Windows Firewall Rule for Local CCTV API (Port 5892)"; GroupDescription: "Network Configuration:"

[Files]
; Dist files compiled by PyInstaller
Source: "..\dist\Provenance\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Windows Firewall Inbound Rule Configuration
Filename: "netsh.exe"; Parameters: "advfirewall firewall add rule name=""Provenance CCTV API"" dir=in action=allow protocol=TCP localport=5892 program=""{app}\{#MyAppExeName}"""; Flags: runhidden; Tasks: firewallrule
; Option to launch Provenance after setup completes
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Remove Windows Firewall Rule on Uninstall
Filename: "netsh.exe"; Parameters: "advfirewall firewall delete rule name=""Provenance CCTV API"""; Flags: runhidden

[Code]
var
  ClipsDirPage: TInputDirWizardPage;

procedure InitializeWizard;
begin
  { Create custom interactive page for choosing Video Evidence Storage Location }
  ClipsDirPage := CreateInputDirPage(
    wpSelectDir,
    'Select Video Evidence Storage Directory',
    'Where should recorded packaging video clips and dispute proofs be stored?',
    'Setup will configure Provenance to store 1080p MP4 recordings in the following folder.'#13#10#13#10 +
    'Click Next to accept the default location, or click Browse to select a secondary high-capacity drive.',
    False,
    ''
  );
  ClipsDirPage.Add('');
  ClipsDirPage.Values[0] := 'C:\Provenance\Clips';
end;

function GetClipsDir(Param: String): String;
begin
  Result := ClipsDirPage.Values[0];
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ClipsPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    ClipsPath := ClipsDirPage.Values[0];
    if ClipsPath = '' then
      ClipsPath := 'C:\Provenance\Clips';
    { Ensure directory exists }
    ForceDirectories(ClipsPath);
  end;
end;
