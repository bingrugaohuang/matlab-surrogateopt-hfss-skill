function result = demo_surrogateopt_mock()
% Analytic demonstration only. Requires Global Optimization Toolbox.
% Run in an independent MATLAB session; this never invokes HFSS.
outDir = tempname;
mkdir(outDir);
checkpointFile = fullfile(outDir, 'checkpoint.mat');
opts = optimoptions('surrogateopt', ...
    'MaxFunctionEvaluations', 20, ...
    'MinSurrogatePoints', 6, ...
    'InitialPoints', [0 0; 0.5 -0.5], ...
    'UseParallel', false, ...
    'CheckpointFile', checkpointFile, ...
    'OutputFcn', @showCurrent, ...
    'PlotFcn', [], 'Display', 'off');
save(fullfile(outDir, 'options.mat'), 'opts');
priorRng = rng;
rngCleanup = onCleanup(@() rng(priorRng));
rng(7, 'twister');
[x, fval, exitflag, output, trials] = surrogateopt(@mockObjective, ...
    [-1 -1], [1 1], opts);
assert(isfinite(fval), 'Mock objective returned a non-finite result.');
result = struct('x', x, 'fval', fval, 'exitflag', exitflag, ...
    'output', output, 'trials', trials, 'outDir', outDir);
save(fullfile(outDir, 'result.mat'), 'result');
fprintf('MOCK ONLY. No HFSS calls. Artifacts: %s\n', outDir);
fprintf('Exit flag %d: %s\n', exitflag, output.message);
end

function value = mockObjective(x)
value = (x(1)-0.25)^2 + 2*(x(2)+0.4)^2;
end

function stop = showCurrent(~, optimValues, state)
stop = false;
if strcmp(state, 'iter')
    fprintf('Mock evaluation %d; current Fval %.6g\n', ...
        optimValues.funccount, optimValues.currentFval);
end
end
