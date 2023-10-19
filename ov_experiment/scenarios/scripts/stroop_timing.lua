function initialize(box)
    dofile(box:get_config("${Path_Data}") .. "/plugins/stimulation/lua-stimulator-stim-codes.lua")
    --in second
    -- target_display = box:get_setting(2) --sec
    -- target_nbr = box:get_setting(3)
    -- baseline_duration = box:get_setting(5) --sec
    target_display = 2 --sec
    target_nbr = 1
    baseline_duration = 1.5 --sec
    stim_break = 1 --sec
    color_trigger_list =  {
        OVTK_StimulationId_Label_11, -- red in red
        OVTK_StimulationId_Label_11, -- red in red
        OVTK_StimulationId_Label_11, -- red in red
        OVTK_StimulationId_Label_12, -- red in green
        OVTK_StimulationId_Label_13, -- red in blue
        OVTK_StimulationId_Label_14, -- red in yellow
        OVTK_StimulationId_Label_21, -- green in red
        OVTK_StimulationId_Label_22, -- green in green
        OVTK_StimulationId_Label_22, -- green in green
        OVTK_StimulationId_Label_22, -- green in green
        OVTK_StimulationId_Label_23, -- green in blue
        OVTK_StimulationId_Label_24, -- green in yellow
        OVTK_StimulationId_Label_31, -- blue in red
        OVTK_StimulationId_Label_32, -- blue in green
        OVTK_StimulationId_Label_33, -- blue in blue
        OVTK_StimulationId_Label_33, -- blue in blue
        OVTK_StimulationId_Label_33, -- blue in blue
        OVTK_StimulationId_Label_34, -- blue in yellow
        OVTK_StimulationId_Label_41, -- yellow in red
        OVTK_StimulationId_Label_42, -- yellow in green
        OVTK_StimulationId_Label_43, -- yellow in blue
        OVTK_StimulationId_Label_44, -- yellow in yellow
        OVTK_StimulationId_Label_44, -- yellow in yellow
        OVTK_StimulationId_Label_44, -- yellow in yellow  -----------------
        OVTK_StimulationId_Label_11, -- red in red
        OVTK_StimulationId_Label_11, -- red in red
        OVTK_StimulationId_Label_11, -- red in red
        OVTK_StimulationId_Label_12, -- red in green
        OVTK_StimulationId_Label_13, -- red in blue
        OVTK_StimulationId_Label_14, -- red in yellow
        OVTK_StimulationId_Label_21, -- green in red
        OVTK_StimulationId_Label_22, -- green in green
        OVTK_StimulationId_Label_22, -- green in green
        OVTK_StimulationId_Label_22, -- green in green
        OVTK_StimulationId_Label_23, -- green in blue
        OVTK_StimulationId_Label_24, -- green in yellow
        OVTK_StimulationId_Label_31, -- blue in red
        OVTK_StimulationId_Label_32, -- blue in green
        OVTK_StimulationId_Label_33, -- blue in blue
        OVTK_StimulationId_Label_33, -- blue in blue
        OVTK_StimulationId_Label_33, -- blue in blue
        OVTK_StimulationId_Label_34, -- blue in yellow
        OVTK_StimulationId_Label_41, -- yellow in red
        OVTK_StimulationId_Label_42, -- yellow in green
        OVTK_StimulationId_Label_43, -- yellow in blue
        OVTK_StimulationId_Label_44, -- yellow in yellow
        OVTK_StimulationId_Label_44, -- yellow in yellow
        OVTK_StimulationId_Label_44, -- yellow in yellow
    }
    math.randomseed(os.time())
    if(math.random(0,1)> 0.5)
    then
        blocks  = {'D', 'ND','D','ND'}
    else
        blocks = {'ND', 'D', 'ND', 'D'}
    end
    distractor_triggers ={
        OVTK_StimulationId_Label_D1,
        OVTK_StimulationId_Label_D2,
        OVTK_StimulationId_Label_D3,
        OVTK_StimulationId_Label_D4
    }
end
function wait_until(box, time)
    while box:get_current_time() < time do
      box:sleep()
    end
  end
function pause_stroop(box)
    while box:keep_processing() do
        --box:log("Trace", string.format("made it 1111111111"))
        -- loops on all inputs of the box
        input_count = box:get_input_count()
        -- box:log("Trace", string.format("Input count: %d", input_count))
        for input = 1, input_count do
            -- box:log("Trace", string.format("made it 22222222"))
            -- loops on every received stimulation for a given input
            for stimulation = 1, box:get_stimulation_count(input) do
                -- gets the received stimulation
                identifier, date, duration = box:get_stimulation(input, 1)
                -- logs the received stimulation
                -- box:log("Trace", string.format("At time %f %f on input %i got stimulation id:%s date:%s duration:%s",t,  t, input, identifier, date, duration))
                box:log("Trace", "foo")
                -- discards it
                box:remove_stimulation(input, 1)
                -- triggers a new OVTK_StimulationId_Label_00 stimulation five seconds after
                --box:send_stimulation(1, OVTK_StimulationId_Label_00, t+5, 0)
                if identifier == OVTK_StimulationId_Number_1B
                then
                    return date
                end
            end
        end
        wait_until(box, box:get_current_time() + 0.5)
        box:sleep()
    end
end
function process(box)
    local function Shuffle(list)
        local s = {}
        for i = 1, #list do s[i] = list[i] end
        for i = #list, 2, -1 do
            local j = math.random(i)
            s[i], s[j] = s[j], s[i]
        end
        return s
    end
    local t=0
    -- manages baseline
    box:send_stimulation(1, OVTK_StimulationId_ExperimentStart, t, 0) -- Instruction 1
    -- todo: add Instrcution image
    t = t + 5
    box:send_stimulation(1, OVTK_GDF_Start, t, 0)
    -- todo: instruction
    box:send_stimulation(1, OVTK_StimulationId_Label_00, t, 0)  -- Instruction 2
    t = t + 5
    box:send_stimulation(1, OVTK_StimulationId_Label_01, t, 0)  -- Instruction 3
    t = t + 5
    for b = 1, #blocks do
        Shuffled_color_list = Shuffle(color_trigger_list)
        box:send_stimulation(1, OVTK_StimulationId_Label_02, t, 0)  -- start of a block
        date = pause_stroop(box)
        t = date + 1
    -- manages trials
        for i = 1, target_nbr do
            -- start of trial
            if blocks[b] == 'D'
            then
                -- -- pick a random index
                box:log("Trace",distractor_triggers)
                box:send_stimulation(1, distractor_triggers[math.random(4)] , t, 0)
            end
            -- FIXATION POINT
            box:send_stimulation(1, OVTK_GDF_Cross_On_Screen, t, 0)
            t = t + baseline_duration
            -- show red in red
            box:send_stimulation(1, Shuffled_color_list[i], t, 0)
            t = t + target_display
            if blocks[b] == 'D'
            then
                -- stop sound
                box:send_stimulation(1,OVTK_StimulationId_Label_D0  , t, 0)
            end
            -- ends trial
            box:send_stimulation(1,OVTK_StimulationId_VisualStimulationStop  , t, 0)
            t =  t+ stim_break
        end
        box:send_stimulation(1, OVTK_StimulationId_Label_03, t, 0)  -- end of the block
        t = t + 3
    end
    box:send_stimulation(1, OVTK_GDF_End_Of_Session, t, 0)
    -- used to cause the acquisition scenario to stop
    box:send_stimulation(1, OVTK_StimulationId_ExperimentStop, t, 0)
    t = t + 3
end