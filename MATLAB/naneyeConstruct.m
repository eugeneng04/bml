function naneye = naneyeConstruct()

    asm = NET.addAssembly('mscorlib');
    NET.addAssembly([pwd '\awcorecs.dll']);
    NET.addAssembly([pwd '\CesysProvider.dll']);
    NET.addAssembly([pwd '\AwFrameProcessing.dll']);


    disp('....Application Starting')
    Awaiba.Drivers.Grabbers.Location.Paths.SetFpgaFilesDirectory('')
    Awaiba.Drivers.Grabbers.Location.Paths.SetBinFile('nanousb2_fpga_v07.bin')
    naneye1 = Awaiba.Drivers.Grabbers.NanEye2DNanoUSB2Provider;
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

    %{
    BW = 0;
    isAECon = naneye1.AutomaticExpControl().IsEnabled;
    isROIon = naneye1.AutomaticExpControl().ShowROI;
    isCOLORon = colorlist.colorReconstruction.Apply;
    %}

    %naneye1.StartCapture();
    naneye = naneye1;
    return;
end
