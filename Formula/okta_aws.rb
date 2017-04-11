class OktaAws < Formula
  include Language::Python::Virtualenv

  desc "Okta AWS API tool"
  homepage "https://github.com/chef/okta_aws"
  url "https://github.com/chef/okta_aws/archive/v0.1.0.tar.gz"
  sha256 "29aa7e55596e5feb3d4e67cd0fcbefdb8ef8c0e97c3ebc881623daf4ecd84f7e"

  depends_on :python

  resource "oktaauth" do
    url "https://files.pythonhosted.org/packages/95/11/8c2d4fce3d6e70841386989f1a227da2028d2cc329b6f816584e2f86c492/oktaauth-0.2.tar.gz"
    sha256 "1615aecb856679c4551915a70a0baa306f7597570d02e0b07734eb2161584c02"
  end

  resource "beautifulsoup4" do
    url "https://files.pythonhosted.org/packages/9b/a5/c6fa2d08e6c671103f9508816588e0fb9cec40444e8e72993f3d4c325936/beautifulsoup4-4.5.3.tar.gz"
    sha256 "b21ca09366fa596043578fd4188b052b46634d22059e68dd0077d9ee77e08a3e"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/16/09/37b69de7c924d318e51ece1c4ceb679bf93be9d05973bb30c35babd596e2/requests-2.13.0.tar.gz"
    sha256 "5722cd09762faa01276230270ff16af7acf7c5c45d623868d9ba116f15791ce8"
  end

  resource "toml" do
    url "https://files.pythonhosted.org/packages/5c/b2/8a18ced00a43f2cc5261f9ac9f1c94621251400a80db1567177719355177/toml-0.9.2.tar.gz"
    sha256 "b3953bffe848ad9a6d554114d82f2dcb3e23945e90b4d9addc9956f37f336594"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/okta_aws --help"
  end
end
