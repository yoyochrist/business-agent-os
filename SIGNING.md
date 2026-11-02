# Release signing guide

This project currently publishes **unsigned** PyInstaller executables. Signing is not performed merely by running the build workflow. **Do not turn off SmartScreen or Gatekeeper as an installation prerequisite.**

## Windows: code-sign before publishing
1. Register an organization/individual publisher identity and set up [Microsoft Artifact Signing](https://learn.microsoft.com/en-us/azure/artifact-signing/overview) or obtain a trusted OV code-signing certificate.
2. Store signing configuration in protected GitHub environments/secrets, never in source files.
3. Grant the GitHub Actions job narrowly scoped OIDC permissions only when integrating Artifact Signing.
4. Build the final executable, sign it using the supported Artifact Signing integration or SignTool, and verify the signature:
   ```powershell
   signtool verify /pa /v dist/BusinessAgentOS-Windows.exe
   ```
5. Publish only the verified signed output; do not modify it after signing.

**Note:** Signed binaries may still trigger SmartScreen until application/publisher reputation builds. OV and EV no longer guarantee an immediate SmartScreen bypass. Microsoft Store distribution is the most consistent way to avoid SmartScreen download warnings.

## macOS: Developer ID and notarization
1. Join the Apple Developer Program and generate a **Developer ID Application** certificate. Export its private key to a securely handled password-protected `.p12`.
2. In a protected GitHub Actions environment, supply the encrypted certificate and password, Apple team ID, and either App Store Connect API key details or app-specific password.
3. Build a native `.app` bundle with PyInstaller `--windowed` and a stable bundle identifier, rather than distributing a bare Mach-O binary.
4. Import the certificate into a temporary CI keychain. Sign the entire application with hardened runtime, using a secure Developer ID identity:
   ```bash
   codesign --force --deep --options runtime --timestamp --sign "$DEVELOPER_ID_APPLICATION" "dist/BusinessAgentOS.app"
   codesign --verify --deep --strict --verbose=2 "dist/BusinessAgentOS.app"
   ```
   Note: `--deep` is not a replacement for correctly signing nested code; ensure PyInstaller dependencies are signed appropriately.
5. Archive the signed app for notarization:
   ```bash
   ditto -c -k --keepParent "dist/BusinessAgentOS.app" "BusinessAgentOS-notarize.zip"
   xcrun notarytool submit "BusinessAgentOS-notarize.zip" --keychain-profile "business-agent-os-notary" --wait
   ```
6. After Apple accepts it, staple the ticket to the **app bundle**:
   ```bash
   xcrun stapler staple "dist/BusinessAgentOS.app"
   xcrun stapler validate "dist/BusinessAgentOS.app"
   spctl --assess --type execute --verbose "dist/BusinessAgentOS.app"
   ```
7. Package a final user-friendly DMG containing the stapled app, verify Gatekeeper on a clean Mac, and publish the verified distribution asset.

Apple Developer ID must not be confused with an ad-hoc or Mac App Store certificate. Test the resulting app in a fresh macOS environment.

## Linux
Publish SHA-256 checksums for the final release artifacts and optionally sign a checksum manifest using a documented public signing key.

## Release gates (recommended)
- Only publish signed artifacts if signing and verification succeeded.
- If signing isn't configured, label the build **UNSIGNED PREVIEW** and do not market it as warning-free.
- Use protected GitHub environments for signing credentials and release approval.
- Sign after building; notarize after macOS signing; publish only after verification.
- Never store certificate private keys or Apple passwords in git.

## Current status
Signing credentials and verified identity are **not configured** in this repository. The automated build workflow remains unsigned. These steps are a maintainer runbook, not proof that signing or notarization has occurred.
