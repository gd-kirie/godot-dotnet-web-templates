using Godot;

namespace Step1CSharpWeb;

public partial class Main : Control
{
    private int _clickCount;
    private Label _counter = null!;

    public override void _Ready()
    {
        var background = new ColorRect
        {
            Color = new Color("101827"),
        };
        background.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        AddChild(background);

        var content = new VBoxContainer
        {
            Alignment = BoxContainer.AlignmentMode.Center,
        };
        content.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        content.OffsetLeft = 48;
        content.OffsetTop = 48;
        content.OffsetRight = -48;
        content.OffsetBottom = -48;
        AddChild(content);

        var title = new Label
        {
            Text = "Godot C# runs in the browser",
            HorizontalAlignment = HorizontalAlignment.Center,
        };
        title.AddThemeFontSizeOverride("font_size", 36);
        content.AddChild(title);

        var details = new Label
        {
            Text = "Godot 4.7.2 · .NET 10 · WebAssembly",
            HorizontalAlignment = HorizontalAlignment.Center,
        };
        details.AddThemeColorOverride("font_color", new Color("8bd5ff"));
        details.AddThemeFontSizeOverride("font_size", 20);
        content.AddChild(details);

        _counter = new Label
        {
            Text = "C# clicks: 0",
            HorizontalAlignment = HorizontalAlignment.Center,
        };
        _counter.AddThemeFontSizeOverride("font_size", 24);
        content.AddChild(_counter);

        var button = new Button
        {
            Text = "Increment C# counter",
            CustomMinimumSize = new Vector2(280, 58),
        };
        button.Pressed += IncrementCounter;
        content.AddChild(button);

        var proof = new Label
        {
            Text = $"Runtime proof: {System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription}",
            HorizontalAlignment = HorizontalAlignment.Center,
        };
        proof.AddThemeColorOverride("font_color", new Color("9aa8bc"));
        proof.AddThemeFontSizeOverride("font_size", 16);
        content.AddChild(proof);

        GD.Print(proof.Text);
        GD.Print(_counter.Text);
    }

    private void IncrementCounter()
    {
        _clickCount += 1;
        _counter.Text = $"C# clicks: {_clickCount}";
        GD.Print(_counter.Text);
    }
}
