function initialize(box)
    dofile(box:get_config("${Path_Data}") .. "/plugins/stimulation/lua-stimulator-stim-codes.lua")

    num_trials = box:get_setting(2)
    stimulus_duration = 2 --sec
    baseline_duration = 1.5 --sec
    break_duration = 1 --sec

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

local function wait_for_continue(box)
    -- loop until box:keep_processing() returns zero
	-- cpu will be released with a call to sleep
	-- at the end of the loop
    while box:keep_processing() do

        -- specify the stimulation that implies to stop waiting
        local target_stimulation = OVTK_StimulationId_Number_1B

        -- get current simulated time
        local t = box:get_current_time()

        -- loop through all inputs of the box
        for input = 1, box:get_input_count() do

            -- loop through every received stimulation for the input
            for stimulation = 1, box:get_stimulation_count(input) do

                -- get the received stimulation and discard it
                local identifier, _, _ = box:get_stimulation(input, 1)
                box:remove_stimulation(input, 1)

                -- return the time if the target stimulation is was received
                if identifier == target_stimulation then
                    return t
                end

            end

        end

        -- release cpu
        box:sleep()
    end
end

local function shuffle_arr(arr)
    local s = {}

    -- copy original array
    for k, _ in ipairs(arr) do
        s[k] = arr[k]
    end

    -- shuffle the copied array
    for i = #arr, 2, -1 do
        local j = math.random(i)
        s[i], s[j] = s[j], s[i]
    end

    return s
end

local function wait_until(box, time)
    while box:get_current_time() < time do
      box:sleep()
    end
end

-- this function is called once by the box
function process(box)

	local t = box:get_current_time()

    -- start the experiment
    box:send_stimulation(1, OVTK_StimulationId_ExperimentStart, t, 0)

    -- display the instructions
    local instructions = {
        OVTK_StimulationId_Label_01,    -- displays instruction 1
        OVTK_StimulationId_Label_02,    -- displays instruction 2
        OVTK_StimulationId_Label_03     -- displays instruction 3
    }
    for k, stim in ipairs(instructions) do
        box:send_stimulation(1, stim, t, 0)
        t = wait_for_continue(box)
    end

    -- iterate through blocks
    for k_b, block in ipairs(blocks) do

        t = box:get_current_time()

        -- prepare the trials for this block
        local trials = {}

        local shuffled_color_triggers = shuffle_arr(color_trigger_list)
        for k = 1, num_trials do
            trials[k] = shuffled_color_triggers[k]
        end

        local trial_type_stim = {}

        for k, trial in ipairs(trials) do

            if ((trial ==  OVTK_StimulationId_Label_11) or (trial ==  OVTK_StimulationId_Label_22)
            or  (trial ==  OVTK_StimulationId_Label_33) or (trial ==  OVTK_StimulationId_Label_44)) then
                if block == 'D' then
                    trial_type_stim[k] =  OVTK_StimulationId_Label_06 -- congruent D trial
                else
                    trial_type_stim[k] =  OVTK_StimulationId_Label_07 -- congruent ND trial
                end    
            else
                if block == 'D' then
                    trial_type_stim[k] =  OVTK_StimulationId_Label_08 -- Non congruent D trial
                else
                    trial_type_stim[k] =  OVTK_StimulationId_Label_09 -- Non congruent ND trial
                end
            end        
        end


        local sounds = {}
        for k, _ in ipairs(trials) do
            -- play sounds only in distractor (D) blocks
            if block == 'D' then
                --TODO: dont hardcode number of distractor triggers
                sounds[k] = distractor_triggers[math.random(4)]
            else
                sounds[k] = OVTK_StimulationId_Label_D0
            end
        end

        t = box:get_current_time() -- time reset

        -- display instructions and wait until indicated to start the block
        box:send_stimulation(1, OVTK_StimulationId_Label_04, t, 0)
        t = wait_for_continue(box)
        box:send_stimulation(1, OVTK_StimulationId_SegmentStart, t, 0)

        --iterate through trials
        for k_t, trial in ipairs(trials) do

            -- assume that at start of loop, `t` is the time of the start of 
            -- the trial

            -- additional steps are performed for distractor (D) blocks

            -- start the trial
            if block == 'D' then
                -- play the sound for this trial
                box:send_stimulation(1, sounds[k_t], t, 0)
            end

            -- show the fixation point for collecting baseline
            box:send_stimulation(1, OVTK_GDF_Cross_On_Screen, t, 0)
            t = t + baseline_duration

            -- show the stimulus
            box:send_stimulation(1, trial, t, 0)
            box:send_stimulation(1, trial_type_stim[k_t], t, 0)
            
            t = t + stimulus_duration

            -- end the trial and wait for a time before starting the next trial
            if block == 'D' then
                -- stop playing the sound
                box:send_stimulation(1, OVTK_StimulationId_Label_D0, t, 0)
            end
            box:send_stimulation(1, OVTK_StimulationId_VisualStimulationStop, t, 0)
            t = t + break_duration

        end

        -- end the block
        box:send_stimulation(1, OVTK_StimulationId_SegmentStop, t, 0)
        box:send_stimulation(1, OVTK_StimulationId_Label_05, t, 0)
        t = t + 3
        wait_until(box, t)
    end

    -- end the experiment
    box:send_stimulation(1, OVTK_StimulationId_ExperimentStop, t, 0)
end