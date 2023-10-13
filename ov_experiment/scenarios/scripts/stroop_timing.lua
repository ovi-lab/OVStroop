function initialize(box)
    dofile(box:get_config("${Path_Data}") .. "/plugins/stimulation/lua-stimulator-stim-codes.lua")
    -- Global variables
    alea_before_warn_min = 100 --msec
    alea_before_warn_max = 1000 --msec
    answer_wait = 1.200 --sec
    time_warn_stim = 400/1000 --sec
    --in second
    target_display = box:get_setting(2) --sec
    target_nbr = box:get_setting(3)
    warning = box:get_setting(4)
    target_stim = _G[box:get_setting(5)]
    baseline_duration = box:get_setting(6) --sec
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
    target_nbr = 1 -- for now
    -- manages trials
    for i = 1, target_nbr do
        -- start of trial
        box:send_stimulation(1, OVTK_GDF_Start_Of_Trial, t, 0)
        box:send_stimulation(1, OVTK_StimulationId_BaselineStart, t, 0)
        t = t + baseline_duration
        box:send_stimulation(1, OVTK_StimulationId_BaselineStop, t, 0)
        -- show red in red
        box:send_stimulation(1, OVTK_StimulationId_Label_11, t, 0)
        t = t + target_display
        -- ends trial
        box:send_stimulation(1, OVTK_GDF_End_Of_Trial, t, 0)
    end
    -- used to cause the acquisition scenario to stop
    box:send_stimulation(1, OVTK_StimulationId_ExperimentStop, t, 0)
end