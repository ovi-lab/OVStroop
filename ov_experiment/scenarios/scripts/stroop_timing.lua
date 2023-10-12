
function initialize(box)
	dofile(box:get_config("${Path_Data}") .. "/plugins/stimulation/lua-stimulator-stim-codes.lua")

	file = io.open("foo.csv", "r")	
	print(file:read())
	file:close()
	
	-- Global variables
	alea_before_warn_min = 100 --msec
	alea_before_warn_max = 1000 --msec
	answer_wait = 1.200 --sec
	time_warn_stim = 400/1000 --sec
	
	--in minute
	xp_duration = box:get_setting(2) --sec 
	--in second
	target_display = box:get_setting(3)/1000 --sec 
	target_nbr = box:get_setting(4)
	warning = box:get_setting(5)
	target_stim = _G[box:get_setting(6)]
	baseline_duration = box:get_setting(7) --sec
	
	trials_duration = xp_duration / target_nbr --sec
		
	-- initializes random seed
	math.randomseed(os.time())
end

function process(box)

	local t=0

	-- manages baseline

	box:send_stimulation(1, OVTK_StimulationId_ExperimentStart, t, 0)
	t = t + 5

	box:send_stimulation(1, OVTK_StimulationId_BaselineStart, t, 0)
	box:send_stimulation(1, OVTK_StimulationId_Beep, t, 0)
	t = t + baseline_duration

	box:send_stimulation(1, OVTK_StimulationId_BaselineStop, t, 0)
	box:send_stimulation(1, OVTK_StimulationId_Beep, t, 0)
	t = t + 5

	-- manages trials
	for i = 1, target_nbr do
	
		-- start of trial
		box:send_stimulation(1, OVTK_GDF_Start_Of_Trial, t, 0)
		
		-- random time before warning
		alea1 = math.random(0, trials_duration*1000-(answer_wait*1000+alea_before_warn_max+time_warn_stim*1000))/1000
		t = t + alea1
		
		-- if warning before stimulus
		if warning == "true" then
			box:send_stimulation(1, OVTK_StimulationId_Beep, t, 0)
		end
		t = t + time_warn_stim
		
		-- random time before target
		alea2 = math.random(alea_before_warn_min, alea_before_warn_max)/1000
		t = t + alea2
		
		-- display target
		box:send_stimulation(1, target_stim, t, 0)
		t = t + target_display
		box:send_stimulation(1, OVTK_StimulationId_VisualStimulationStop, t, 0)
		
		-- wait for the end of trial
		wait = (trials_duration - alea1 - time_warn_stim - alea2) --sec
		t = t + wait
		
		
		-- ends trial 
		box:send_stimulation(1, OVTK_GDF_End_Of_Trial, t, 0)
	end

	-- send end for completeness
	box:send_stimulation(1, OVTK_GDF_End_Of_Session, t, 0)
	t = t + 5

	box:send_stimulation(1, OVTK_StimulationId_Train, t, 0)
	t = t + 1
	
	-- used to cause the acquisition scenario to stop
	box:send_stimulation(1, OVTK_StimulationId_ExperimentStop, t, 0)

end
