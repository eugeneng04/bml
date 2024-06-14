function featureoutput = setSensorFeature(valuein,y)
% This function will limit the maximum allowed values of each register.
%
bitval=valuein;

    switch y
        case 1
            % Gain
            bitval(bitval<0) = 0;
            bitval(bitval>3) = 3;
        case 2
            % Offset 
            bitval(bitval<0) = 0;
            bitval(bitval>3) = 3;
        case 3
            % Exposure
            bitval(bitval<1) = 1;
            bitval(bitval>250) = 250;
        case 4
            % Supply Voltage - recommended to be 1700 min value and 2400
            % max value
            bitval(bitval<1) = 1;
            bitval(bitval>2400) = 2400;
%             
%         case 5
%             
%             bitval(bitval<0) = 0;
%             bitval(bitval>1) = 1;
%             
        case 5
            % LED Voltage
            bitval(bitval<0) = 0;
            bitval(bitval>4096) = 4096;
%             
%         case 7
%             bitval(bitval<0) = 0;
%             bitval(bitval>1) = 1;
%             
%         case 8
%             %Show ROI
%             bitval(bitval<0) = 0;
%             bitval(bitval>1) = 1;



 
    end
featureoutput=bitval;

