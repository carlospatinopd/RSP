clear
clc

% angulos para describir la esfera de Bloch
phi = 0:pi/128:2*pi;
theta = 0:pi/128:pi;

% fidelidad RSP
fidelities = fidelity_map(theta, phi);

% resultado
figure('Position', [100, 100, 800, 600])
imagesc(phi, theta, fidelities)
axis([0 2*pi 0 pi])
axis xy
colormap(bone)
clim([0 1])
set(gca, 'FontSize', 12)
xlabel('\phi', 'FontSize', 24)
ylabel('\theta', 'FontSize', 24)
colorbar
c = colorbar;
c.Label.String = 'Fidelidad';
c.FontSize = 14;
c.Label.FontSize = 28;
saveas(gcf, 'fidelidad_estimada.png')

function F = RSP(th, phi)
    q0 = [1; 0]; % estado 0
    q1 = [0; 1]; % estado 1
    m = [cos(th/2); sin(th/2)*exp(1i*phi)]'; % estado objetivo

    % compuertas cuanticas
    I = [1 0; 0 1]; % identidad
    X = [0 1; 1 0]; % pauli X
    Z = [1 0; 0 -1]; % pauli Z
    H = [1 1; 1 -1]/sqrt(2); % hadamard
    CX = [1 0 0 0; 0 1 0 0; 0 0 0 1; 0 0 1 0]; % control X
    Ry = [cos(th/2) -sin(th/2); sin(th/2) cos(th/2)]'; % rotacion en y
    P = [1 0; 0 exp(1i*phi)]'; % rotacion en z
    rot = Ry*P; % rotacion simplificada

    % preparacion estado de Bell
    psi = kron(q0,q0);
    psi = kron(X,X)*psi;
    psi = kron(H,I)*psi;
    psi = CX*psi;

    % medicion en base arbitraria
    psi = kron(rot,I)*psi;
    B0 = kron(q0',I)*psi; % bob si alice obtiene 0
    B1 = kron(q1',I)*psi; % bob si alice obtiene 1
    
    % si el resultado de la medicion es 0
    B0 = Z*B0;
    B0 = X*B0;
    P0 = norm(B0)^2;
    B0 = B0/sqrt(P0);
    
    % si el resultado de la medicion es 1
    P1 = norm(B1)^2;
    B1 = B1/sqrt(P1);
 
    % fidelidad del estado preparado con el estado objetivo
    F0 = abs(m*B0)^2;
    F1 = abs(m*B1)^2;
    F = P0*F0+P1*F1;
end

function fidelities = fidelity_map(theta, phi)
    fidelities = zeros(length(theta), length(phi));
    for ip = 1:length(phi)
        for it = 1:length(theta)
            fidelities(it, ip) = RSP(theta(it), phi(ip));
            fprintf('theta=%.2f, phi=%.2f, P(0)=%.4f\n', theta(it), phi(ip), fidelities(it, ip));
        end
    end
end