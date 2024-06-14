function initNaneye()
    %{
        disp("initializing device");
        streamNaneyeImage(true);
    %}
    disp("running camera");
    streamNaneyeImage(false);
end
