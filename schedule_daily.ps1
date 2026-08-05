# PowerShell script para agendar a execução diária do Agente de Tendências no Windows.
# Executa todos os dias às 08:00 AM em segundo plano.

$TaskName = "TechTrendsAudioDigestDaily"
$ProjectPath = "E:\Projetos\tendencias_tecnologia"
$PythonPath = (Get-Command python).Source

Write-Host "Configurando Agendamento Diário do Agente de IA..." -ForegroundColor Cyan

# Define a ação de execução
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "src\main.py" -WorkingDirectory $ProjectPath

# Define o gatilho diário (às 08:00 AM)
$Trigger = New-ScheduledTaskTrigger -Daily -At 08:00AM

# Registra ou substitui a tarefa agendada
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Description "Agente de IA que gera diariamente o resumo em áudio das tendências de tecnologia." -Force

Write-Host "✅ Tarefa '$TaskName' agendada com sucesso para rodar todos os dias às 08:00 AM!" -ForegroundColor Green
Write-Host "Para testar manualmente a tarefa agendada:" -ForegroundColor Yellow
Write-Host "Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
