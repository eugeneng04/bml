function naneyetest2()
    global naneye1 w h colorlist BW hbytes % Declare hbytes as global here

    lock = -1;

    if exist('asm') ~= 1
        asm = NET.addAssembly('mscorlib');
    end

    NET.addAssembly([pwd '\awcorecs.dll']);
    NET.addAssembly([pwd '\CesysProvider.dll']);
    NET.addAssembly([pwd '\AwFrameProcessing.dll']);


    disp('....Application Starting')

    Awaiba.Drivers.Grabbers.Location.Paths.SetFpgaFilesDirectory('')
    Awaiba.Drivers.Grabbers.Location.Paths.SetBinFile('nanousb2_fpga_v07.bin')

    naneye1 = Awaiba.Drivers.Grabbers.NanEye2DNanoUSB2Provider; w=250; h=250;

    SensorReg = load('NaneyeRegDataUSB2.mat');

    SensorDefault = load('NaneyeRegDataUSB2_default.mat');

    for i = 1:8
        regobj = Awaiba.Drivers.Grabbers.NanEyeRegisterPayload(false, i, true, 0, cell2mat(SensorDefault.RegData(i,4)));
        naneye1.WriteRegister(regobj)
    end

    naneye1.AutomaticExpControl().ShowROI = 0;
    naneye1.AutomaticExpControl().Enabled = 0;
    colorlist = Awaiba.FrameProcessing.ProcessingWrapper.Instance(0);
    colorlist.colorReconstruction.Apply = 1;

    BW = 0;
    global hbytes
    naneye1.StartCapture();
    lh1 = addlistener(naneye1, 'ImageProcessed', @(o,e)ouputObj(e));

    while true
        disp(getData());
    end
end


function ouputObj(inbytes)
    global hbytes
    hbytes = uint8(inbytes.GetImageData.GetProcessedDataARGBByte);
end

function output = getData()
   global hbytes
   output = hbytes;
   return;
end
